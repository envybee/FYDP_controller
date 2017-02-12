from MotorController import MCInterface

mc = MCInterface()

while True:
	mc.forwardM0(149)
	mc.forwardM1(149)
