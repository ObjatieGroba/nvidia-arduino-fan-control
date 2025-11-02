from .arduino_tools import Nano
from .nvidia_tools import NvidiaSMI
from .configuration import Configuration

import time
import argparse
import sys
from pathlib import Path

DEFAULT_PROFILE_PATH = Path(__file__).absolute().parent / 'default_profile.json'

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--autoupdate', action='store_true')
parser.add_argument('-p', '--profile', default=DEFAULT_PROFILE_PATH)

args = parser.parse_args()

config = Configuration.load(args.profile)

smi = NvidiaSMI()
controller = Nano(autoupdate=args.autoupdate)

cur_flow = -1
speed_decrease_deadline: float | None = None

while True:
    start_time = time.time()
    info = smi.get_info()

    new_flow = config.get_flow(info)

    if new_flow != cur_flow:
        if new_flow < cur_flow and speed_decrease_deadline is None:
            print(f'Set {new_flow}, prev {cur_flow}. Hold {config.step_down_threshold_seconds} seconds', file=sys.stderr)
            speed_decrease_deadline = start_time + config.step_down_threshold_seconds
        if new_flow > cur_flow or (speed_decrease_deadline is not None and speed_decrease_deadline <= start_time):
            print(f'Set {new_flow}, prev {cur_flow}', file=sys.stderr)
            if controller.set_pwm(new_flow):
                cur_flow = new_flow
                last_flow_change_time = start_time
                speed_decrease_deadline = None
            else:
                print('Can not set fan speed...', file=sys.stderr)
    else:
        speed_decrease_deadline = None

    elapsed_time = time.time() - start_time
    if elapsed_time > config.update_interval_seconds:
        print(f'Operation took too long: {elapsed_time} seconds...', file=sys.stderr)
    else:
        time.sleep(config.update_interval_seconds - elapsed_time)
