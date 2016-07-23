import serial
import time
from MotorController import MCInterface
import threading
from motion_detector_camshift import newData
global dataBuffer

#Constants - Ki, Kd, Kp
Kp = 10
Ki = 10
Kd = 10

mc = MCInterface()
cL = controllerLoop(1, mc)

cL.start()

class controllerLoop(threading.Thread):
    def __init__(self, threadID,  mc):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = mc
        #Initialize
        self.prevTime = None
        
    def run(self):
        
        while True:
            if(newData is None):
                continue
            (currVelocity, currTime) = newData
            currVelocity = currVelocity*127
            newData = None
            currVelocity = int(currVelocity*63)
            #Record the time
            if(self.prevTime is None):
                prevTime = currTime
                prevError = error
                prevVelocity = currVelocity
                intError = error
                continue

            error = currVelocity - prevVelocity
            prevVelocity = currVelocity
            
            deltaT = currTime - prevTime
            self.prevTime = currTime

            diffError = (error - prevError)/deltaT
            prevError = error

            intError = prevError + (error * deltaT)

            currVelocity = Kp * error + Kd * diffError + Ki * intError
            
            self.mc.forwardM0(currVelocity)
            self.mc.forwardM1(currVelocity)