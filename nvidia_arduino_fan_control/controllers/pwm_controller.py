class PWMController:
    def __init__(self, name: str, min_speed: int | None = None, max_speed: int | None = None):
        self.name = name
        self.min_speed = min_speed
        self.max_speed = max_speed

    def _get(self) -> int | None:
        raise NotImplementedError

    def _set(self, flow: float):
        raise NotImplementedError

    def get(self) -> int | None:
        """
        :return: rps
        """
        return self._get()

    def set(self, flow: float) -> float:
        """
        accept flow from 0.0 to 1.0
        :return: None
        """
        if self.min_speed is not None and flow < self.min_speed / 100:
            flow = self.min_speed / 100
        if self.max_speed is not None and flow > self.max_speed / 100:
            flow = self.max_speed / 100
        self._set(flow)
        return flow
