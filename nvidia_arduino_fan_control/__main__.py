import argparse
from pathlib import Path

from .flow_control import FlowController

DEFAULT_PROFILE_PATH = Path(__path__).absolute() / 'default_profile.yaml'

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--profile', default=DEFAULT_PROFILE_PATH)

args = parser.parse_args()

controller = FlowController(args.profile)
controller.run()
