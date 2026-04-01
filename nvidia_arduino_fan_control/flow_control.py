import yaml
import time
import sys
from dataclasses import dataclass

from .sensors import Sensor, HWMonSensor, NvidiaSensor
from .controllers import NanoController, HWMonController, PWMController
from .configuration import Configuration, HWMonSensorDescr, NvidiaSensorDescr, HWMonFanDescr, ArduinoFanDescr


@dataclass
class SensorInfo:
    sensor: Sensor
    last_value: int = 0
    last_printed_value: int = 0


@dataclass
class FanInfo:
    controller: PWMController
    windowed_values: list[float]
    prev: float = -1.


class FlowController:
    def __init__(self, cnf_path: str):
        with open(cnf_path) as f:
            self.config = Configuration.parse_obj(yaml.safe_load(f))

        self.sensors: dict[str, SensorInfo] = {}
        for sensor in self.config.sensors:
            if sensor.name in self.sensors:
                raise ValueError(f'Sensor {sensor.name} duplicated')

            if isinstance(sensor, HWMonSensorDescr):
                self.sensors[sensor.name] = SensorInfo(HWMonSensor.get_by_label(sensor.hwmon, sensor.label or sensor.name))
            elif isinstance(sensor, NvidiaSensorDescr):
                self.sensors[sensor.name] = SensorInfo(NvidiaSensor(sensor.sensor, sensor.filter))
            else:
                raise ValueError(f'Sensor {sensor.name} ({sensor.type}) is not supported')

        self.fans: dict[str, FanInfo] = {}
        for fan in self.config.fans:
            if fan.name in self.fans:
                raise ValueError(f'Fan {fan.name} duplicated')

            if isinstance(fan, HWMonFanDescr):
                self.fans[fan.name] = FanInfo(HWMonController.get_by_label(fan.hwmon, fan.label or fan.name, fan.min, fan.max), [])
            elif isinstance(fan, ArduinoFanDescr):
                self.fans[fan.name] = FanInfo(NanoController(fan.port, fan.autoupdate, fan.min, fan.max), [])
            else:
                raise ValueError(f'Fan {fan.name} ({fan.type}) is not supported')

        for controller in self.config.controllers:
            if controller.sensor not in self.sensors:
                raise ValueError(f'Sensor {controller.sensor} not found')
            if controller.fan not in self.fans:
                raise ValueError(f'Fan {controller.fan} not found')

    def _update_sensors(self, start_time: float):
        for name, sensor in self.sensors.items():
            try:
                sensor.last_value = sensor.sensor.get(start_time)
                if abs(sensor.last_value - sensor.last_printed_value) > 5:
                    print(f'Sensor {name}: {sensor.last_value}', file=sys.stderr)
                    sensor.last_printed_value = sensor.last_value
            except Exception as e:
                print(f'Sensor {name} failed to read: {type(e)} - {e}', file=sys.stderr)

    def _update_fans(self):
        for fan in self.fans.values():
            fan.windowed_values.append(0.)
            if len(fan.windowed_values) >= self.config.window_intervals:
                fan.windowed_values = fan.windowed_values[1:]

        for controller in self.config.controllers:
            value = self.sensors[controller.sensor].last_value
            fan_speed = controller.get(value)
            self.fans[controller.fan].windowed_values[-1] = max(fan_speed, self.fans[controller.fan].windowed_values[-1])

        for name, fan in self.fans.items():
            new = max(fan.windowed_values)
            if fan.prev != new:
                print(f'Set {name} from {fan.prev} to {new}. RPM: {fan.controller.get()}', file=sys.stderr)
                fan.controller.set(new)
                fan.prev = new

    def run(self):
        while True:
            start_time = time.time()
            self._update_sensors(start_time)
            self._update_fans()
            time_taken = time.time() - start_time
            if time_taken > self.config.update_interval_seconds:
                print(f'Too long update time: {time_taken} > {self.config.update_interval_seconds}', file=sys.stderr)
            else:
                time.sleep(self.config.update_interval_seconds - time_taken)
