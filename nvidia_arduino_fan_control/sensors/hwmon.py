from .sensor import Sensor

import glob


class HWMonSensor(Sensor):
    def __init__(self, hwmon: str, idx: int, tpe: str = 'temp'):
        self.hwmon = hwmon
        self.idx = idx
        self.type = tpe

    @property
    def path(self) -> str:
        return f'/sys/class/hwmon/{self.hwmon}'

    @property
    def label(self) -> str:
        with open(f'{self.path}/{self.type}{self.idx}_label') as f:
            return f.read().strip()

    def get(self, _: float) -> int:
        with open(f'{self.path}/{self.type}{self.idx}_input') as f:
            return int(f.read().strip()) // 1000

    @staticmethod
    def get_by_label(hwmon: str, label: str) -> 'HWMonSensor':
        idx = HWMonSensor.labels(hwmon)[label]
        return HWMonSensor(hwmon, idx)

    @staticmethod
    def labels(hwmon: str, tpe: str = 'temp') -> dict[str, int]:
        res = {}
        for label_path in glob.glob(f'/sys/class/hwmon/{hwmon}/{tpe}*_label'):
            with open(label_path) as f:
                label = f.read().strip()
                res[label] = int(label_path[label_path.rfind('/') + 1:].removesuffix('_label').removeprefix(tpe))
        return res
