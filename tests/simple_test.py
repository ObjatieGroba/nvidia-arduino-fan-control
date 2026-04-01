from nvidia_arduino_fan_control import TempPoint, Controller

c = Controller(sensor='', fan='', points=[TempPoint(temp=10, flow=10)], mode='stair')
assert c.get(9) == 0.10
assert c.get(10) == 0.10
assert c.get(11) == 0.10


c = Controller(sensor='', fan='', points=[TempPoint(temp=10, flow=10)], mode='slope')
assert c.get(9) == 0.10
assert c.get(10) == 0.10
assert c.get(11) == 0.10


c = Controller(sensor='', fan='', points=[TempPoint(temp=10, flow=10), TempPoint(temp=20, flow=20)], mode='stair')
assert c.get(9) == 0.10
assert c.get(10) == 0.10
assert c.get(11) == 0.10
assert c.get(19) == 0.10
assert c.get(20) == 0.20
assert c.get(21) == 0.20


c = Controller(sensor='', fan='', points=[TempPoint(temp=10, flow=10), TempPoint(temp=20, flow=20)], mode='slope')
assert c.get(9) == 0.10
assert c.get(10) == 0.10
assert c.get(11) == 0.11
assert c.get(19) == 0.19
assert c.get(20) == 0.20
assert c.get(21) == 0.20
