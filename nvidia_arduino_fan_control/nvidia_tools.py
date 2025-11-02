import subprocess
import dataclasses


@dataclasses.dataclass
class GpuInfo:
    name: str
    temp: int
    fan_speed_perc: int


class NvidiaSMI:
    EXECUTABLE = 'nvidia-smi'

    def __init__(self, executable: str = EXECUTABLE):
        self.executable = executable

    def get_info(self) -> list[GpuInfo]:
        r = subprocess.run([self.executable, '--query-gpu=name,temperature.gpu,fan.speed', '--format=csv,noheader,nounits'],
                           capture_output=True, encoding='utf-8')

        def process(line: str) -> tuple[str, int, int]:
            name, temp, speed = line.split(', ')
            return name, int(temp), int(speed)

        return [GpuInfo(*process(line)) for line in r.stdout.splitlines()]
