from MotorController import MCInterface
import threading
from msvcrt import getch

CONST_VELOCITY = 5

class Inputs(threading.Thread):
    def __init__(self, data_queue, threadID):
        self.data_queue = data_queue
        self.establish_connection()
        self.mc = MCInterface()

        threading.Thread.__init__(self)
        self.threadID = threadID

    def get_data(self):
        key = ord(getch())
        if key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(getch())
            if key == 80: #Down arrow
                self.reverse()
            elif key == 72: #Up arrow
                self.forward()
            elif key == 75: #Left turn
                self.turn_left
            elif key == 77:
                self.turn_right #Right Arrow

    def turn_left():
        self.mc.forwardM0(CONST_VELOCITY)
        self.mc.forwardM0(CONST_VELOCITY)

    def turn_right():
        self.mc.reverseM1(CONST_VELOCITY)
        self.mc.reverseM1(CONST_VELOCITY)

    def forward():
        self.mc.forwardM0(CONST_VELOCITY)
        self.mc.reverseM1(CONST_VELOCITY)

    def reverse():
        normVel = abs(int(2*CONST_VELOCITY))
        self.mc.reverseM0(normVel)
        self.mc.forwardM1(normVel)

    def establish_connection(self):
        pass

    def run(self):
        while True:
            data = self.get_data()
            self.logger.info("Received: " + data)
            self.populate_queue(data)

    def populate_queue(self, data):
        self.data_queue.put(data)

    def normalize(self):
        pass