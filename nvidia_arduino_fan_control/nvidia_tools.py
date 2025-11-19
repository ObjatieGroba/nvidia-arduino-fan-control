import subprocess
import dataclasses


@dataclasses.dataclass
class GpuInfo:
    name: str
    temp: int
    fan_speed_perc: int
    pstate: str
    cur_power_w: float


class NvidiaSMI:
    EXECUTABLE = 'nvidia-smi'

    def __init__(self, executable: str = EXECUTABLE):
        self.executable = executable

    def get_info(self) -> list[GpuInfo]:
        r = subprocess.run([self.executable, '--query-gpu=name,temperature.gpu,fan.speed,pstate,power.draw', '--format=csv,noheader,nounits'],
                           capture_output=True, encoding='utf-8')

        def process(line: str) -> GpuInfo:
            name, temp, speed, pstate, power = line.split(', ')
            return GpuInfo(name, int(temp), int(speed), pstate, float(power))

        return [process(line) for line in r.stdout.splitlines()]
