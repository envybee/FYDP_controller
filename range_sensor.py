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
    def __init__(self, threadID, med_data_value, logger):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.avgSampleSize = 25
        self.distanceValues = [0 for x in range(self.avgSampleSize)]

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

        self.reference_distance = 30

        self.kill_received = False

    def running_mean(self):
        window = 10
        weights = np.repeat(1.0, window)/window
        sma = np.convolve(self.distanceValues, weights, 'valid')

        return int(sma[len(sma) - 1])


    def isValid(self, cur_value, ind):
        if ind < 1:
            return self.distanceValues[0]
            
        df = cur_value - self.distanceValues[ind - 1]
        speed = df/0.2

        return speed < 250

    def run(self):
        distance = 0 
        distance2 = 0
        count = 0
        ind = 0
        mean = 0
        while not self.kill_received:
            ind = count % self.avgSampleSize

            distance = self.getRangeFromSensor(0)
            self.logger.info("Sensor " + str(1) + " Iteration: " + str(count) + "Distance : {0:5.1f}".format(distance))

            distance2 = self.getRangeFromSensor(1)
            self.logger.info("Sensor " + str(2) + " Iteration: " + str(count) + "Distance : {0:5.1f}".format(distance2))

            distToSend = int(min(distance, distance2))

            if not self.isValid(distToSend, ind):
                continue

            distToSend = self.running_mean()
            self.logger.info("Filtered Medial Value --> " + str(distToSend))

            self.med_data_value[0] = distToSend
            self.distanceValues[ind] = distToSend

            time.sleep(0.2)
            count = count + 1

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
        stop = time.time()

        while GPIO.input(ECHO_Arr[sensorNum])==0:
          start = time.time()
          stop = time.time()

        while GPIO.input(ECHO_Arr[sensorNum])==1:
          stop = time.time()

        # Calculate pulse length
        elapsed = stop-start

        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (cm/s)
        distance = elapsed * speedSound

        # That was the distance there and back so halve the value
        distance = distance / 2
        
        return distance
        


