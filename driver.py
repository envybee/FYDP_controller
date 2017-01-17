
import logging
import signal
import sys

from Queue import Queue
from controller import ControllerLoop
from recieve_inputs import Inputs

def main():
    logger = logging.getLogger(__name__)

    input_queue = Queue()

    # Initialize controller module
    cL = ControllerLoop(1, input_queue, logger)

    # Initialize input handler
    inputs = Inputs()

    # Cleanup on Ctrl+C
    signal.signal(signal.SIGINT, sigint_handler)

    cL.start()

def sigint_handler(signum, frame):
    cL.kill_received = True
    sys.exit(0)

if __name__ == "__main__":
    main()