import pynvml
import dataclasses
import typing as tp

from .sensor import Sensor


@dataclasses.dataclass
class GpuInfo:
    name: str
    temp: int
    cur_power_w: int


class NvidiaSensors:
    def __init__(self):
        pynvml.nvmlInit()
        self.num_of_devices = pynvml.nvmlDeviceGetCount()
        devices = [
            pynvml.nvmlDeviceGetHandleByIndex(i)
            for i in range(self.num_of_devices)
        ]
        self.devices = [
            (pynvml.nvmlDeviceGetName(device), device)
            for device in devices
        ]
        self.prev: tuple[float, list[GpuInfo]] | None = None

    def get_info(self, cur_time: float | None = None) -> list[GpuInfo]:
        if self.prev is not None and self.prev[0] == cur_time:
            return self.prev[1]
        res: list[GpuInfo] = []
        for name, device in self.devices:
            temp = pynvml.nvmlDeviceGetTemperatureV(device, pynvml.NVML_TEMPERATURE_GPU)
            cur_power = pynvml.nvmlDeviceGetPowerUsage(device) // 1000
            res.append(GpuInfo(name, temp, cur_power))
        if cur_time is not None:
            self.prev = cur_time, res
        return res


sensors: NvidiaSensors | None = None


class NvidiaSensor(Sensor):
    def __init__(self, tpe: tp.Literal['temp', 'power'], flt: str | None = None):
        self.type = tpe
        self.filter = flt

    def get(self, cur_time: float) -> int:
        global sensors
        if sensors is None:
            sensors = NvidiaSensors()
        infos = [
            info for info in sensors.get_info(cur_time)
            if self.filter in info.name
        ]
        if not infos:
            raise RuntimeError("Empty list")
        if self.type == 'temp':
            return max(info.temp for info in infos)
        if self.type == 'power':
            return max(info.cur_power_w for info in infos)
        raise RuntimeError(f"Unknown sensor type {self.type}")
