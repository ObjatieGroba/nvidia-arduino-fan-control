from .arduino_tools import MAX_FLOW
from .nvidia_tools import GpuInfo

import dataclasses
import json
from dataclass_wizard import JSONWizard


ALLOWED_MODES = ('slope', 'stair')


@dataclasses.dataclass
class TempPoint(JSONWizard):
    temp: int
    flow: int


@dataclasses.dataclass
class Configuration(JSONWizard):
    temp_points: list[TempPoint]
    gpu_fan_active_threshold_flow: int
    step_down_threshold_seconds: float
    update_interval_seconds: float
    mode: str

    def __post_init__(self):
        if self.mode not in ALLOWED_MODES:
            raise ValueError(f'Unsupported mode: {self.mode}. Allowed modes are {ALLOWED_MODES}')
        for i in range(len(self.temp_points) - 1):
            if self.temp_points[i].temp >= self.temp_points[i + 1].temp:
                raise ValueError(f'Expected ascending temp points: {self.temp_points[i].temp} < {self.temp_points[i + 1].temp}')
            if self.temp_points[i].flow > self.temp_points[i + 1].flow:
                raise ValueError(f'Expected ascending flow points: {self.temp_points[i].flow} <= {self.temp_points[i + 1].flow}')
        for point in self.temp_points:
            if point.flow > MAX_FLOW:
                raise ValueError(f'Flow should not be greater than {MAX_FLOW} - {point.flow}')
        if self.gpu_fan_active_threshold_flow > MAX_FLOW:
            raise ValueError(f'Flow should not be greater than {MAX_FLOW} - {self.gpu_fan_active_threshold_flow}')

    def get_flow(self, info: list[GpuInfo]) -> int:
        max_temp = max(i.temp for i in info)
        fan_active = any(i.fan_speed_perc for i in info)

        next_point_idx = next((i for i in range(len(self.temp_points)) if self.temp_points[i].temp > max_temp), len(self.temp_points))
        cur_point = self.temp_points[next_point_idx - 1] if next_point_idx > 0 else self.temp_points[0]
        if self.mode == 'stair':
            new_flow = cur_point.flow
        elif self.mode == 'slope':
            if cur_point.temp >= max_temp:
                new_flow = cur_point.flow
            elif next_point_idx < len(self.temp_points):
                next_point = self.temp_points[next_point_idx]
                new_flow = cur_point.flow + int((max_temp - cur_point.temp) * (next_point.flow - cur_point.flow) / (next_point.temp - cur_point.temp))
            else:
                new_flow = self.temp_points[-1].flow
        else:
            raise NotImplementedError()

        if fan_active:
            new_flow = max(new_flow, self.gpu_fan_active_threshold_flow)

        return new_flow

    @staticmethod
    def load(path: str) -> 'Configuration':
        with open(path, 'r') as f:
            return Configuration.from_dict(json.load(f))
