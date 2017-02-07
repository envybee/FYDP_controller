from MotorController import MCInterface
import threading
import curses

CONST_VELOCITY = 50


class Inputs(threading.Thread):
    def __init__(self, threadID, med_dist, lat_dist, logger):
        self.med_dist = med_dist
        self.lat_dist = lat_dist

        threading.Thread.__init__(self)

        # self.establish_connection()
        self.mc = MCInterface()
        self.logger = logger

        self.threadID = threadID

        # get the curses screen window
        self.screen = curses.initscr()

        # turn off input echoing
        curses.noecho()

        # respond to keys immediately (don't wait for enter)
        curses.cbreak()

        # map arrow keys to special values
        self.screen.keypad(True)

    def get_data(self):
        char = self.screen.getch()
        return char

    def turn_left(self, CONST_VELOCITY):
        self.mc.forwardM0(CONST_VELOCITY)
        self.mc.forwardM0(CONST_VELOCITY)

    def turn_right(self, CONST_VELOCITY):
        self.mc.reverseM1(CONST_VELOCITY)
        self.mc.reverseM1(CONST_VELOCITY)

    def forward(self, CONST_VELOCITY):
        self.mc.forwardM0(CONST_VELOCITY)
        self.mc.reverseM1(CONST_VELOCITY)

    def reverse(self, CONST_VELOCITY):
        normVel = abs(int(2*CONST_VELOCITY))
        self.mc.reverseM0(normVel)
        self.mc.forwardM1(normVel)

    def establish_connection(self):
        pass

    # Runs on inputs.start()
    def run(self):
        try:
            while True:
                char = self.get_data()
                self.logger.info("Received: " + str(char))
                if char == ord('q'):
                    break
                elif char == curses.KEY_RIGHT:
                    # print doesn't work with curses, use addstr instead
                    self.screen.addstr(0, 0, 'right')
                    self.lat_dist[0] = 50
                elif char == curses.KEY_LEFT:
                    self.screen.addstr(0, 0, 'left ')
                    self.lat_dist[0] = -50
                elif char == curses.KEY_UP:
                    self.screen.addstr(0, 0, 'up   ')
                    self.med_dist[0] = 50
                elif char == curses.KEY_DOWN:
                    self.screen.addstr(0, 0, 'down ')
                    self.med_dist[0] = -50

        finally:
            # shut down cleanly
            curses.nocbreak()
            self.screen.keypad(0)
            curses.echo()
            curses.endwin()
