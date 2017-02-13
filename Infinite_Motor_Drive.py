from MotorController import MCInterface

mc = MCInterface()

for i in range(0, 149, 5):
	mc.forwardM0(i)
	mc.forwardM1(i)

for i in range(149, 0, -5):
	mc.forwardM0(i)
	mc.forwardM1(i)

mc.forwardM0(0)
mc.forwardM1(0)