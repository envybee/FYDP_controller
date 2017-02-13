from MotorController import MCInterface
from time import sleep

mc = MCInterface()

for i in range(0, 20, 3):
	mc.forwardM0(i)
	mc.forwardM1(i)
	sleep(1)

for i in range(20, 0, -3):
	mc.forwardM0(i)
	mc.forwardM1(i)
	sleep(1)

mc.forwardM0(0)
mc.forwardM1(0)