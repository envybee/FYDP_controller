
import logging
import signal
import sys

from controller import ControllerLoop
from recieve_inputs import Inputs
from vision_subsystem import Vision_Subsystem
from range_sensor import Ultrasonic

import threading

from time import sleep

def sigint_handler(signum, frame):
    cL.kill_received = True
    vision.kill_received = True
    #ultrasonic.kill_received = True

    sys.exit(0)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    file_hdlr = logging.FileHandler('/var/log/controller.log')
    logger.addHandler(file_hdlr)

    logger.setLevel(logging.DEBUG)

    med_value = [0]
    lat_value = [0]

    # Initialize threads
    ultrasonic = Ultrasonic(3, med_value, logger)
    cL = ControllerLoop(1, med_value, lat_value, logger)
    # inputs = Inputs(2, med_value, lat_value, logger)
    #vision = Vision_Subsystem(1, lat_value, logger, False)

    # Cleanup on Ctrl+C
    signal.signal(signal.SIGINT, sigint_handler)

    # Set threads to run in daemon mode so they can be killed
    cL.daemon = True
    # inputs.daemon = True
    #vision.daemon = True
    ultrasonic.daemon = True

    # Start all the threads
    cL.start()
    # inputs.start()
    #vision.start()
    ultrasonic.start()

    while threading.activeCount() > 0:
        sleep(0.1)

