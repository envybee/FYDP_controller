import serial
import time


#Command

#Controller automatically adjusts baud rate based on the baud rate at which this command is sent
CONTROLLER_AUTODETECT = 0xAA 

GET_FIRMWARE_VERSION = 0x81
GET_ERROR_BYTE = 0x82

GET_CONFIG_PARAM = 0x83
SET_CONFIG_PARAM = 0x84
                       
M0_VARIABLE_BRAKE = 0x86
M1_VARIABLE_BRAKE = 0X87

M0_MOVE_FORWARD = 0x88
M0_MOVE_FORWARD_8BIT = 0x89
M0_MOVE_REVERSE = 0x8A
M0_MOVE_REVERSE_8BIT = 0x8B


M1_MOVE_FORWARD = 0x8C
M1_MOVE_FORWARD_8BIT = 0x8D
M1_MOVE_REVERSE = 0x8E
M1_MOVE_REVERSE_8BIT = 0x8F

M0_GET_CURRENT = 0x90
M1_GET_CURRENT = 0x91

M0_GET_SPEED = 0x92
M1_GET_SPEED = 0x93


# Configuration parameters
#QIK_CONFIG_DEVICE_ID =  0
#QIK_CONFIG_PWM_PARAMETER =  1
#QIK_CONFIG_SHUT_DOWN_MOTORS_ON_ERROR =  2
#QIK_CONFIG_SERIAL_TIMEOUT =  3

class MCInterface:

	def __init__(self,**kwargs):

		port=kwargs.get('serialPort', "/dev/ttyAMA0")
		baudRate = int(kwargs.get('baudRate', 9600))

		#Set the serial port and baud rate, while also clearing the input buffer
		self.serialport = serial.Serial(port, baudRate)
		time.sleep(1)
		self.serialport.flushInput()

		self.message = bytearray()
		self.is8bit = bool(kwargs.get('is8bit', False))

		#Establish contact with the motor controller
		self.establishConnection()

	def establishConnection(self):
		del self.message[:]
		self.message.append(CONTROLLER_AUTODETECT)
		self.serialport.write(self.message)

	def forwardM0(self, speed):
		del self.message[:]
		if speed < 0:
			speed = 0

		if self.is8bit:
			if speed > 255:
				speed = 255

			speed = speed - 128
			self.message.append(M0_MOVE_FORWARD)

		else:
			if speed > 127:
				speed = 127

			self.message.append(M0_MOVE_FORWARD_8BIT)		
		self.message.append(speed)
		self.serialport.write(self.message)

	def forwardM1(self, speed):
		
		del self.message[:]

		if speed < 0:
			speed = 0

		if self.is8bit:
			if speed > 255:
				speed = 255

			speed = speed - 128
			self.message.append(M1_MOVE_FORWARD)

		else:
			if speed > 127:
				speed = 127

			self.message.append(M1_MOVE_FORWARD_8BIT)		

		self.message.append(speed)
		self.serialport.write(self.message)


	def reverseM0(self, speed):
		
		del self.message[:]

		if speed < 0:
			speed = 0

		if self.is8bit:
			if speed > 255:
				speed = 255

			speed = speed - 128
			self.message.append(M0_MOVE_REVERSE)

		else:
			if speed > 127:
				speed = 127

			self.message.append(M0_MOVE_REVERSE_8BIT)		

		self.message.append(speed)
		self.serialport.write(self.message)

	def reverseM1(self, speed):
		
		del self.message[:]

		if speed < 0:
			speed = 0

		if self.is8bit:
			if speed > 255:
				speed = 255

			speed = speed - 128
			self.message.append(M1_MOVE_REVERSE)

		else:
			if speed > 127:
				speed = 127

			self.message.append(M1_MOVE_REVERSE_8BIT)		

		self.message.append(speed)
		self.serialport.write(self.message)

	def setVelocity(self, velocity):
		self.setVelocityM0(velocity)
		self.setVelocityM1(velocity)

	def setVelocityM0(self, velocity):

		if velocity > 0:
			self.forwardM0(velocity)
		elif velocity < 0:
			self.reverseM0(velocity)

	def setVelocityM1(self, velocity):

		if velocity > 0:
			self.forwardM1(velocity)
		elif velocity < 0:
			self.reverseM0(velocity)



