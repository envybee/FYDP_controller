
import logging
import signal
import sys

from controller import ControllerLoop
from recieve_inputs import Inputs
from vision_subsystem import Vision_Subsystem
from range_sensor import Ultrasonic
from bluetooth_interface import Bluetooth

import threading

from time import sleep

def sigint_handler(signum, frame):
    cL.kill_received = True
    #vision.kill_received = True
    ultrasonic.kill_received = True
    bt_interface.kill_received = True

    sys.exit(0)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    file_hdlr = logging.FileHandler('/var/log/controller.log')
    logger.addHandler(file_hdlr)

    logger.setLevel(logging.INFO)

    med_value = [0]
    lat_value = [0]

    bt_signal = [True]

    # Initialize threads
    #bt_interface = Bluetooth(logger, bt_signal)
    ultrasonic = Ultrasonic(3, med_value, logger, bt_signal)
    cL = ControllerLoop(1, med_value, lat_value, logger, bt_signal)
    # inputs = Inputs(2, med_value, lat_value, logger)
    #vision = Vision_Subsystem(1, lat_value, logger, False)

    # Cleanup on Ctrl+C
    signal.signal(signal.SIGINT, sigint_handler)

    # Set threads to run in daemon mode so they can be killed
    cL.daemon = True
    # inputs.daemon = True
    #vision.daemon = True
    ultrasonic.daemon = True
    #bt_interface.daemon = True

    # Start all the threads
    #bt_interface.start()
    cL.start()
    # inputs.start()
    #vision.start()
    ultrasonic.start()

    while threading.activeCount() > 0:
        sleep(0.1)

    logger.info("Exiting")
