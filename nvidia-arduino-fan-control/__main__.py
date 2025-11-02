from .arduino_tools import Nano, MAX_FLOW
from .nvidia_tools import NvidiaSMI

import time
import argparse
import sys
import json
import dataclasses
from pathlib import Path
from dataclass_wizard import JSONWizard

DEFAULT_PROFILE_PATH = Path(__file__).absolute().parent / 'default_profile.json'
ALLOWED_MODES = ('slope', 'stair')

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--autoupdate', action='store_true')
parser.add_argument('-p', '--profile', default=DEFAULT_PROFILE_PATH)

args = parser.parse_args()


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


with open(args.profile, 'r') as f:
    config = Configuration.from_dict(json.load(f))

smi = NvidiaSMI()
controller = Nano(autoupdate=args.autoupdate)

cur_flow = -1
speed_decrease_deadline: float | None = None

while True:
    start_time = time.time()
    infos = smi.get_info()
    max_temp = max(i.temp for i in infos)
    fan_active = any(i.fan_speed_perc for i in infos)

    next_point_idx = next((i for i in range(len(config.temp_points)) if config.temp_points[i].temp >= max_temp), None)
    cur_point = config.temp_points[next_point_idx - 1] if next_point_idx else config.temp_points[0]
    if config.mode == 'stair':
        new_flow = cur_point.flow
    elif config.mode == 'slope':
        if cur_point.temp >= max_temp:
            new_flow = cur_point.flow
        elif next_point_idx is not None:
            next_point = config.temp_points[next_point_idx]
            new_flow = cur_point.flow + int((max_temp - cur_point.temp) * (next_point.flow - cur_point.flow) / (next_point.temp - cur_point.temp))
        else:
            new_flow = config.temp_points[-1].flow
    else:
        raise NotImplementedError()

    if fan_active:
        new_flow = max(new_flow, config.gpu_fan_active_threshold_flow)

    if new_flow != cur_flow:
        if new_flow < cur_flow and speed_decrease_deadline is None:
            print(f'Set {new_flow}, prev {cur_flow} after {config.step_down_threshold_seconds} seconds', file=sys.stderr)
            speed_decrease_deadline = start_time + config.step_down_threshold_seconds
        if new_flow > cur_flow or speed_decrease_deadline <= start_time:
            print(f'Set {new_flow}, prev {cur_flow}', file=sys.stderr)
            if not controller.set_pwm(new_flow):
                print('Can not set fan speed...', file=sys.stderr)
            else:
                cur_flow = new_flow
                last_flow_change_time = start_time
                speed_decrease_deadline = None
    else:
        speed_decrease_deadline = None

    elapsed_time = time.time() - start_time
    if elapsed_time > config.update_interval_seconds:
        print(f'Operation took too long: {elapsed_time} seconds...', file=sys.stderr)
    else:
        time.sleep(config.update_interval_seconds - elapsed_time)
