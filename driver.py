
import logging
import signal
import sys

from Queue import Queue
from controller import ControllerLoop
from recieve_inputs import Inputs
from vision_subsystem import Vision_Subsystem

def main():
    logger = logging.getLogger(__name__)
    file_hdlr = logging.FileHandler('/var/log/controller.log')
    logger.addHandler(file_hdlr)

    logger.setLevel(logging.DEBUG)

    med_value = [0]
    lat_value = [0]

    # Initialize controller module
    cL = ControllerLoop(1, med_value, lat_value, logger)

    # Initialize input handler
    inputs = Inputs(2, med_value, lat_value, logger)

    vision = Vision_Subsystem(1, lat_value, logger, False)

    # Cleanup on Ctrl+C
    #signal.signal(signal.SIGINT, main.sigint_handler)

    cL.start()
    inputs.start()
    #vision.start()

    def sigint_handler(signum, frame):
        cL.kill_received = True
        sys.exit(0)

if __name__ == "__main__":
    main()
