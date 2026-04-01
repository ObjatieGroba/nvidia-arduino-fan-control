from pydantic import BaseModel, Field
import typing as tp


class TempPoint(BaseModel):
    temp: int
    flow: int


class SensorDescrBase(BaseModel):
    name: str
    type: tp.Literal['hwmon', 'nvidia']


class HWMonSensorDescr(SensorDescrBase):
    type: tp.Literal['hwmon']
    hwmon: str
    label: str | None = None


class NvidiaSensorDescr(SensorDescrBase):
    type: tp.Literal['nvidia']
    sensor: tp.Literal['temp', 'power'] = 'temp'
    filter: str | None = None
    
    
SensorDescr = tp.Annotated[
    tp.Union[HWMonSensorDescr, NvidiaSensorDescr],
    Field(discriminator="type")
]


class FanDescrBase(BaseModel):
    name: str
    type: tp.Literal['hwmon', 'arduino']
    min: int | None = None
    max: int | None = None


class HWMonFanDescr(FanDescrBase):
    type: tp.Literal['hwmon']
    hwmon: str
    label: str | None = None


class ArduinoFanDescr(FanDescrBase):
    type: tp.Literal['arduino']
    port: str | None = None
    autoupdate: bool = False


FanDescr = tp.Annotated[
    tp.Union[HWMonFanDescr, ArduinoFanDescr],
    Field(discriminator="type")
]


class Controller(BaseModel):
    sensor: str
    fan: str

    points: list[TempPoint]
    mode: tp.Literal['slope', 'stair'] = 'slope'

    def get(self, value: int) -> float:
        idx = 0
        for point in self.points:
            if point.temp > value:
                break
            idx += 1

        cur = self.points[idx - 1] if idx > 0 else self.points[0]

        if self.mode == 'stair':
            return cur.flow / 100

        nxt = self.points[idx] if idx < len(self.points) else self.points[-1]

        if nxt.temp == cur.temp:
            return nxt.flow / 100
        return (cur.flow + (value - cur.temp) * (nxt.flow - cur.flow) / (nxt.temp - cur.temp)) / 100


class Configuration(BaseModel):
    sensors: list[SensorDescr]
    fans: list[FanDescr]
    controllers: list[Controller]
    update_interval_seconds: float = 0.5
    window_intervals: int = 4
