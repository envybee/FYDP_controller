from MotorController import MCInterface
from time import sleep

mc = MCInterface()

for i in range(0, 149, 5):
	mc.forwardM0(i)
	mc.forwardM1(i)
	sleep(0.2)

for i in range(149, 0, -5):
	mc.forwardM0(i)
	mc.forwardM1(i)
	sleep(0.2)

mc.forwardM0(0)
mc.forwardM1(0)