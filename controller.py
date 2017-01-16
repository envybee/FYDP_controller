import serial
import time
from MotorController import MCInterface
import threading

class controllerLoop(threading.Thread):
    def __init__(self, threadID,  mc, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = mc
        #Initialize
        self.prevTime = None

        self.Kp = 1.5
        self.Ki = 0.3
        self.Kd = 0.7
        self.dataQueue = q
        self.kill_received = False

    def setVelocity(self, currVelocity):
        if(currVelocity > 0):
            self.mc.forwardM0(currVelocity)
            self.mc.reverseM1(currVelocity)
        else:
            normVel = abs(int(2*currVelocity))
            self.mc.reverseM0(normVel)
            self.mc.forwardM1(normVel)

    def run(self):
        firstRun = True
        while (True and not self.kill_received):

            if(self.dataQueue.empty()):
                continue
            (error, currTime) = self.dataQueue.get()

            print("%.2f" % round(error,2), "Queue: " + str(self.dataQueue.queue))
            
            #Record the time
            if(self.prevTime is None):
                self.prevTime = currTime
                prevError = error
                intError = error
                continue

            deltaT = (currTime - self.prevTime)*100
            self.prevTime = currTime

            #error = currVelocity - prevVelocity
            #print(error, currVelocity, prevVelocity, deltaT)

            #if(abs(error/prevVelocity) > 0.5):
            #   continue

            diffError = (error - prevError)/deltaT
            intError = prevError + (error * deltaT)
            prevError = error

            #print(diffError, intError)

            currVelocity = self.Kp * error + self.Kd * diffError + self.Ki * intError        
            currVelocity = int(currVelocity)

            if(-5 < currVelocity and currVelocity < 5):
                currVelocity = 0

            if(firstRun):
                firstRun = False
                for i in range(1,currVelocity,10) :
                    self.setVelocity(i)
            
            self.setVelocity(currVelocity)
            
            print("Tuned & normalized velocity  " + str(currVelocity))


        if(self.kill_received):
            self.mc.forwardM0(0)
            self.mc.forwardM1(0)
