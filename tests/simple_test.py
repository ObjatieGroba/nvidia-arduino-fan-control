from nvidia_arduino_fan_control import Configuration, TempPoint, GpuInfo

c = Configuration([TempPoint(10, 10)], 0, 0, 0, 'stair')
assert c.get_flow([GpuInfo('test', 9, 0)]) == 10
assert c.get_flow([GpuInfo('test', 10, 0)]) == 10
assert c.get_flow([GpuInfo('test', 11, 0)]) == 10
assert c.get_flow([GpuInfo('test', 9, 100)]) == 10
assert c.get_flow([GpuInfo('test', 10, 100)]) == 10
assert c.get_flow([GpuInfo('test', 11, 100)]) == 10


c = Configuration([TempPoint(10, 10)], 0, 0, 0, 'slope')
assert c.get_flow([GpuInfo('test', 9, 0)]) == 10
assert c.get_flow([GpuInfo('test', 10, 0)]) == 10
assert c.get_flow([GpuInfo('test', 11, 0)]) == 10
assert c.get_flow([GpuInfo('test', 9, 100)]) == 10
assert c.get_flow([GpuInfo('test', 10, 100)]) == 10
assert c.get_flow([GpuInfo('test', 11, 100)]) == 10


c = Configuration([TempPoint(10, 10)], 40, 0, 0, 'slope')
assert c.get_flow([GpuInfo('test', 9, 0)]) == 10
assert c.get_flow([GpuInfo('test', 10, 0)]) == 10
assert c.get_flow([GpuInfo('test', 11, 0)]) == 10
assert c.get_flow([GpuInfo('test', 9, 100)]) == 40
assert c.get_flow([GpuInfo('test', 10, 100)]) == 40
assert c.get_flow([GpuInfo('test', 11, 100)]) == 40


c = Configuration([TempPoint(10, 10), TempPoint(20, 20)], 0, 0, 0, 'stair')
assert c.get_flow([GpuInfo('test', 9, 0)]) == 10
assert c.get_flow([GpuInfo('test', 10, 0)]) == 10
assert c.get_flow([GpuInfo('test', 11, 0)]) == 10
assert c.get_flow([GpuInfo('test', 9, 100)]) == 10
assert c.get_flow([GpuInfo('test', 10, 100)]) == 10
assert c.get_flow([GpuInfo('test', 11, 100)]) == 10
assert c.get_flow([GpuInfo('test', 19, 0)]) == 10
assert c.get_flow([GpuInfo('test', 20, 0)]) == 20
assert c.get_flow([GpuInfo('test', 21, 0)]) == 20
assert c.get_flow([GpuInfo('test', 19, 100)]) == 10
assert c.get_flow([GpuInfo('test', 20, 100)]) == 20
assert c.get_flow([GpuInfo('test', 21, 100)]) == 20


c = Configuration([TempPoint(10, 10), TempPoint(20, 20)], 0, 0, 0, 'slope')
assert c.get_flow([GpuInfo('test', 9, 0)]) == 10
assert c.get_flow([GpuInfo('test', 10, 0)]) == 10
assert c.get_flow([GpuInfo('test', 11, 0)]) == 11
assert c.get_flow([GpuInfo('test', 9, 100)]) == 10
assert c.get_flow([GpuInfo('test', 10, 100)]) == 10
assert c.get_flow([GpuInfo('test', 11, 100)]) == 11
assert c.get_flow([GpuInfo('test', 19, 0)]) == 19
assert c.get_flow([GpuInfo('test', 20, 0)]) == 20
assert c.get_flow([GpuInfo('test', 21, 0)]) == 20
assert c.get_flow([GpuInfo('test', 19, 100)]) == 19
assert c.get_flow([GpuInfo('test', 20, 100)]) == 20
assert c.get_flow([GpuInfo('test', 21, 100)]) == 20
