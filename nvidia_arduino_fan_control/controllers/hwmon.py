from .pwm_controller import PWMController

import glob


class HWMonController(PWMController):
    def __init__(self, hwmon: str, idx: int, min_speed: int | None = None, max_speed: int | None = None):
        self.hwmon = hwmon
        self.idx = idx

        super().__init__(self.label or f'{hwmon}/{idx}', min_speed, max_speed)

    @property
    def path(self) -> str:
        return f'/sys/class/hwmon/{self.hwmon}'

    @property
    def label(self) -> str:
        with open(f'{self.path}/fan{self.idx}_label') as f:
            return f.read().strip()

    @property
    def input(self) -> str:
        with open(f'{self.path}/fan{self.idx}_input') as f:
            return f.read().strip()

    def _get(self) -> int | None:
        return int(self.input)

    def _set(self, value: float) -> None:
        int_val = max(min(int(value * 255), 255), 0)
        with open(f'{self.path}/pwm{self.idx}', 'w') as f:
            f.write(str(int_val))

    @staticmethod
    def get_by_label(hwmon: str, label: str, *args) -> 'HWMonController':
        idx = HWMonController.labels(hwmon)[label]
        return HWMonController(hwmon, idx, *args)

    @staticmethod
    def labels(hwmon: str) -> dict[str, int]:
        res = {}
        for label_path in glob.glob(f'/sys/class/hwmon/{hwmon}/fan*_label'):
            with open(label_path) as f:
                label = f.read().strip()
                res[label] = int(label_path[label_path.rfind('/') + 1:].removesuffix('_label').removeprefix('fan'))
        return res
