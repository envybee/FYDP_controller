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
time.sleep(1)
mc.forwardM0(149)
time.sleep(1)
mc.forwardM0(0)
time.sleep(1)
mc.reverseM0(149)
time.sleep(1)
mc.reverseM0(0)
time.sleep(1)
mc.forwardM1(149)
time.sleep(1)
mc.forwardM1(0)
time.sleep(1)
mc.reverseM1(149)
time.sleep(1)
mc.reverseM1(0)


#mc.forwardM0(128)

#time.sleep(1)

#mc.forwardM1(249)

#time.sleep(1)

#mc.forwardM1(128)
