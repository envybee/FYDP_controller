import serial
import time
from MotorController import MCInterface
import threading


# Store necessary values to perform sliding window/Kalman filtering and other filtering
class InputFilter:
    def __init__(self):
        pass

    def filter(self):
        pass


class ControllerLoop(threading.Thread):
    def __init__(self, threadID, med_dist_queue, lat_dist_queue, logger):
        self.logger = logger

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = MCInterface()

        # Initialize
        self.prevTime = None

        self.Kp = 1.5
        self.Ki = 0.3
        self.Kd = 0.7
        self.med_dist_queue = med_dist_queue
        self.lat_dist_queue = lat_dist_queue
        self.kill_received = False

    def setVelocity(self, currVelocity):
        if currVelocity > 0:
            self.mc.forwardM0(currVelocity)
            self.mc.reverseM1(currVelocity)
        else:
            normVel = abs(int(2*currVelocity))
            self.mc.reverseM0(normVel)
            self.mc.forwardM1(normVel)

    def run(self):
        firstRun = True
        while (True and not self.kill_received):

            if(self.med_dist_queue.empty()):
                continue
            (error, currTime) = self.med_dist_queue.get()

            self.logger.debug("%.2f" % round(error,2), "Queue: " + str(self.med_dist_queue.queue))
            
            #Record the time
            if self.prevTime is None:
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

            self.logger.info(diffError, intError)

            currVelocity = self.Kp * error + self.Kd * diffError + self.Ki * intError        
            currVelocity = int(currVelocity)

            if(-5 < currVelocity and currVelocity < 5):
                currVelocity = 0

            if firstRun:
                firstRun = False
                for i in range(1,currVelocity,10) :
                    self.setVelocity(i)
            
            self.setVelocity(currVelocity)
            
            print("Tuned & normalized velocity  " + str(currVelocity))


        if(self.kill_received):
            self.mc.forwardM0(0)
            self.mc.forwardM1(0)
