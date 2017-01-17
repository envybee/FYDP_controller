import RPi.GPIO as GPIO
import time
import Queue
import signal
import sys
import logging
from controller import ControllerLoop

logger = logging.getLogger(__name__)

dataQueue = Queue.Queue()
newData = None

cL = ControllerLoop(1, dataQueue, logger)

def sigint_handler(signum, frame):
    cL.kill_received = True
    GPIO.cleanup()
    sys.exit(0)


GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

logger.info("Starting Control Loop")
cL.start()

logger.info("Distance Measurement In Progress")

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.output(TRIG, False)
logger.info("Waiting For Sensor To Settle")

count = 0

previous_time = time.time()
height_diff = 0
reference_distance = 30
current_distance = 0

signal.signal(signal.SIGINT, sigint_handler)


while True:
	count+=1

	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	while GPIO.input(ECHO)==0:
		logger.debug("waiting for pulse return")
		pulse_start = time.time()

	while GPIO.input(ECHO)==1:
		logger.debug("Waiting for the pulse to go back down")
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start

	distance = pulse_duration * 17150

	current_distance = round(distance, 2)
	current_time = time.time()
	time_diff = current_time - previous_time
	distance_diff = current_distance - reference_distance

	if(distance_diff > reference_distance*5):
		logger.debug("continuing...")
		continue

	speed = float(distance_diff)/(time_diff*100)
	                 
	newData = (speed, current_time)
	dataQueue.put(newData)

	previous_time = current_time

	logger.info("Iteration: ",count,"Distance diff:",distance_diff," cm","  Time Delta:",time_diff," sec")
	time.sleep(0.05)

cL.kill_received = True
GPIO.cleanup()
