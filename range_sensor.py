import RPi.GPIO as GPIO
import time
import signal
from controller import ControllerLoop
import threading
import numpy as np

newData = None

TRIG_Arr = [23, 16]
ECHO_Arr = [24, 20]

class Ultrasonic(threading.Thread):
    def __init__(self, threadID, med_data_value, logger, bt_signal, lat_value):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.avgSampleSize = 25
        #self.distanceValues = [0 for x in range(self.avgSampleSize)]
        self.lat_value = lat_value
        self.bt_signal = bt_signal

        GPIO.setmode(GPIO.BCM)

        self.med_data_value = med_data_value
        self.logger = logger

        logger.debug("Distance Measurement In Progress")

        for TRIG in TRIG_Arr:
            GPIO.setup(TRIG, GPIO.OUT)

        for ECHO in ECHO_Arr:
            GPIO.setup(ECHO, GPIO.IN)

        for TRIG in TRIG_Arr:
            GPIO.output(TRIG, False)

        logger.debug("Waiting Detection...")

        self.reference_distance = 125

        self.kill_received = False

    '''def running_mean(self):
        window = 10
        weights = np.repeat(1.0, window)/window
        sma = np.convolve(self.distanceValues, weights, 'valid')

        return int(sma[len(sma) - 1])'''


    def isValid(self, cur_value):#, prev):

        #df = abs(cur_value - prev)

        #self.logger.info("distance diff ->" + str(df))

        return cur_value < 300# and df < 40

    def run(self):
        prev = 1
        skippedCount = 0
        initVals = []
        
        while self.lat_value[0] is 0:
          pass
        
        #prev = self.getMedianVal(11)
              
          
        while not self.kill_received:
            #ind = count % self.avgSampleSize
              
            distToSend = self.getMedianVal(4)
            self.logger.info("Medial Value --> " + str(distToSend))
            if prev == 0:
                prev = distToSend
                continue

            if not self.isValid(distToSend):#, prev):
                self.logger.info("--SKIPPED--")
                skippedCount += 1
                if skippedCount > 3:
                  self.med_data_value[0] = 0
                  time.sleep(0.05)
            
                continue
                
            skippedCount = 0

            #distToSend = self.running_mean()
            

            self.med_data_value[0] = distToSend - self.reference_distance
            #self.distanceValues[ind] = distToSend

            time.sleep(0.05)

            #prev = distToSend

        GPIO.cleanup()
        
    def getMedianVal(self, tries):
        count = 0
        medianVal = 0
        vals = []
          
        while count < tries:
            #ind = count % self.avgSampleSize
            count += 1

            distance = self.getRangeFromSensor(0)
            time.sleep(0.1)
            distance2 = self.getRangeFromSensor(1)
            
            self.logger.info(str(vals))

            distToSend = int(min(distance, distance2))
            
            vals.append(distToSend)

        vals = sorted(vals)    
        medianVal = vals[int(tries/2)]

        return medianVal
    

    def getRangeFromSensor(self, sensorNum):
        
        # Speed of sound in cm/s at temperature
        temperature = 20
        speedSound = 33100 + (0.6*temperature)

        # Send 10us pulse to trigger
        GPIO.output(TRIG_Arr[sensorNum], True)
        # Wait 10us
        time.sleep(0.00001)
        GPIO.output(TRIG_Arr[sensorNum], False)
        start = time.time()
        stop = time.time()
        
      	while GPIO.input(ECHO_Arr[sensorNum])==0:
      	  stop = time.time()
          start2 = stop
          if stop - start > 1:
            self.logger.debug("Sending TimeOut")
            return 99999
            
        start2 = stop
      	while GPIO.input(ECHO_Arr[sensorNum])==1:
      	  stop = time.time()
          if stop - start2 > 1:
            self.logger.debug("Sending TimeOut")
            return 99999
           

        # Calculate pulse length
        elapsed = stop-start

        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (cm/s)
        distance = elapsed * speedSound

        # That was the distance there and back so halve the value
        distance = distance / 2
        
        return distance
        


