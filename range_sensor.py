import RPi.GPIO as GPIO
import time
import signal
import logging
from controller import ControllerLoop
import threading

newData = None

TRIG = 23
ECHO = 24


class Ultrasonic(threading.Thread):
    def __init__(self, threadID, med_data_value, logger):
        threading.Thread.__init__(self)
        self.threadID = threadID

        GPIO.setmode(GPIO.BCM)

        self.med_data_value = med_data_value
        self.logger = logger

        logger.info("Distance Measurement In Progress")

        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)

        GPIO.output(TRIG, False)
        logger.info("Waiting For Sensor To Settle")

        self.reference_distance = 30

        self.kill_received = False

    def run(self):
        count = 0
        pulse_start = 0
        pulse_duration = 0
        while not self.kill_received:
            count += 1

            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            self.logger.debug("waiting for pulse return")
            while GPIO.input(ECHO) == 0:
                pulse_start = time.time()

            self.logger.debug("Waiting for the pulse to go back down")
            while GPIO.input(ECHO) == 1:
                pulse_end = time.time()
                pulse_duration = pulse_end - pulse_start
                if pulse_duration > 0.01:
                    break

            if pulse_duration > 0.01:
                continue

            self.logger.debug("Pulse duration: " + str(pulse_duration))

            distance = pulse_duration * 17150

            current_distance = round(distance, 2)
            distance_diff = int(current_distance - self.reference_distance)

            self.med_data_value[0] = distance_diff

            self.logger.info("Iteration: " + str(count) + " Distance: " + str(current_distance)
                             + "cm \nDistance diff:" + str(distance_diff) + " cm")
            time.sleep(0.05)

        GPIO.cleanup()
