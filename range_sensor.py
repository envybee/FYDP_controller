import RPi.GPIO as GPIO
import time
import signal
import logging
from controller import ControllerLoop
import threading

newData = None

TRIG_Arr = [23, 16]
ECHO_Arr = [24, 20]

class Ultrasonic(threading.Thread):
    def __init__(self, threadID, med_data_value, logger):
        threading.Thread.__init__(self)
        self.threadID = threadID

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

    def run(self):
        distance = 0 
        distance2 = 0
        count = 0
        while not self.kill_received:
            distance = self.getRangeFromSensor(0)
            self.logger.info("Sensor " + str(1) + " Iteration: " + str(count) + "Distance : {0:5.1f}".format(distance))

            distance2 = self.getRangeFromSensor(1)
            self.logger.info("Sensor " + str(2) + " Iteration: " + str(count) + "Distance : {0:5.1f}".format(distance2))


            self.med_data_value[0] = int(min(distance, distance2))

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

        while GPIO.input(ECHO_Arr[sensorNum])==0:
          start = time.time()

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
        


