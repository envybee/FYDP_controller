from MotorController import MCInterface
from time import sleep

mc = MCInterface()

for i in range(0, 149, 3):
	mc.forwardM0(i)
	mc.forwardM1(i)
	sleep(0.4)
sleep(5)
for i in range(149, 0, -3):
	mc.forwardM0(i)
	mc.forwardM1(i)
	sleep(0.4)

mc.forwardM0(0)
mc.forwardM1(0)
