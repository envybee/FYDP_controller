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
    def __init__(self, threadID, med_data_value, logger, bt_signal):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.avgSampleSize = 25
        #self.distanceValues = [0 for x in range(self.avgSampleSize)]

        self.bt_signal = bt_signal

        GPIO.setmode(GPIO.BCM)

        self.med_data_value = med_data_value
        self.logger = logger

        logger.info("Distance Measurement In Progress")

        for TRIG in TRIG_Arr:
            GPIO.setup(TRIG, GPIO.OUT)

        for ECHO in ECHO_Arr:
            GPIO.setup(ECHO, GPIO.IN)

        for TRIG in TRIG_Arr:
            GPIO.output(TRIG, False)

        logger.info("Waiting For Sensor To Settle")

        self.reference_distance = 50

        self.kill_received = False

    '''def running_mean(self):
        window = 10
        weights = np.repeat(1.0, window)/window
        sma = np.convolve(self.distanceValues, weights, 'valid')

        return int(sma[len(sma) - 1])'''


    def isValid(self, cur_value, prev):

        df = abs(cur_value - prev)

        self.logger.info("distance diff ->" + str(df))

        return df < 30 and cur_value < 300

    def run(self):
        count = 0
        prev = 0
        while not self.kill_received:
            #ind = count % self.avgSampleSize
            count += 1

            distance = self.getRangeFromSensor(0)
            time.sleep(0.1)
            distance2 = self.getRangeFromSensor(1)

            self.logger.info("Sensor " + str(2) + " Iteration: " + str(count) + "Distance : {0:5.1f}".format(distance2))

            distToSend = int(min(distance, distance2))

            if prev == 0:
                prev = distToSend
                continue

            if not self.isValid(distToSend, prev):
                self.logger.info("--SKIPPED--")    
                continue

            #distToSend = self.running_mean()
            self.logger.info("Medial Value --> " + str(distToSend))

            self.med_data_value[0] = distToSend - self.reference_distance
            #self.distanceValues[ind] = distToSend

            time.sleep(0.05)

            prev = distToSend

        GPIO.cleanup()

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
        stop = time
        
      	while GPIO.input(ECHO_Arr[sensorNum])==0:
      	  stop = time.time()
          start2 = stop
          if stop - start > 1:
            self.logger.info("Sending TimeOut")
            return 99999
            
        start2 = stop
      	while GPIO.input(ECHO_Arr[sensorNum])==1:
      	  stop = time.time()
          if stop - start2 > 1:
            self.logger.info("Sending TimeOut")
            return 99999
           

        # Calculate pulse length
        elapsed = stop-start

        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (cm/s)
        distance = elapsed * speedSound

        # That was the distance there and back so halve the value
        distance = distance / 2
        
        return distance
        


