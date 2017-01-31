
import logging
import signal
import sys

from Queue import Queue
from controller import ControllerLoop
from recieve_inputs import Inputs


def main():
    logger = logging.getLogger(__name__)

    med_dist_queue = Queue()
    lat_dist_queue = Queue()

    # Initialize controller module
    cL = ControllerLoop(1, med_dist_queue, lat_dist_queue, logger)

    # Initialize input handler
    inputs = Inputs(2, med_dist_queue, lat_dist_queue, logger)

    # Cleanup on Ctrl+C
    #signal.signal(signal.SIGINT, main.sigint_handler)

    cL.start()
    inputs.start()

    def sigint_handler(signum, frame):
        cL.kill_received = True
        sys.exit(0)

if __name__ == "__main__":
    main()