import serial
import time
from MotorController import MCInterface


#s = serialport = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)
#s.write( chr(0xAA) )
#time.sleep(1)
#s.write( chr(0x88) + chr(50) )  # motor 0 full speed forward
#time.sleep(1)
#s.write( chr(0xA+ chr(0x08) + chr(0) )    # motor 0 speed to 0
#time.sleep(1)
#s.write( chr(0xAA) + chr(0x09) + chr(0x0A) + chr(50) )    # motor 0 full speed reverse
#time.sleep(1)
#s.write( chr(0xAA) + chr(0x09) + chr(0x0A) + chr(0) )      # motor 0 stop


mc = MCInterface()
mc.forwardM0(0)
mc.forwardM1(0)
#for i in range(0, 150, 10):
#	mc.reverseM0(i)
#	mc.forwardM1(i)
#	time.sleep(10)
time.sleep(1)
mc.forwardM0(149)
mc.forwardM1(149)
time.sleep(3)
mc.forwardM0(0)
mc.forwardM1(0)

