import serial
import time
from MotorController import MCInterface
import threading
from motion_detector_camshift import newData

class controllerLoop(threading.Thread):
    def __init__(self, threadID,  mc):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = mc
        #Initialize
        self.prevTime = None

        self.Kp = 10
        self.Ki = 10
        self.Kd = 10

    def run(self):
        
        while True:
            if(newData is None):
                continue
            (currVelocity, currTime) = newData
            newData = None

            print("%.2f" % round(currVelocity,2))
            currVelocity = int(currVelocity*127)
            #Record the time
            if(self.prevTime is None):
                prevTime = currTime
                prevError = error
                prevVelocity = currVelocity
                intError = error
                continue

            deltaT = currTime - prevTime
            self.prevTime = currTime

            error = currVelocity - prevVelocity

            if(abs(error/prevVelocity) > 0.5)
                continue

            prevVelocity = currVelocity        


            diffError = (error - prevError)/deltaT
            intError = prevError + (error * deltaT)
            prevError = error

            currVelocity = self.Kp * error + self.Kd * diffError + self.Ki * intError

            if(-5 < currVelocity and currVelocity < 5):
                currVelocity = 0
            
            #self.mc.forwardM0(currVelocity)
            #self.mc.forwardM1(currVelocity)

            print("Tuned & normalized velocity" + currVelocity)