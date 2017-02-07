from MotorController import MCInterface
import threading
from time import sleep


# Store necessary values to perform sliding window/Kalman filtering and other filtering
class InputFilter:
    def __init__(self, logger):
        # Initialize
        self.logger = logger

        self.prevTime = None

        self.target_vel = 0
        self.cur_vel = 0

        self.Kp = 1
        self.Ki = 0.3
        self.Kd = 0.7

        self.deltaT = 0.01

        self.output_threshold = 5

    def filter(self, target_vel):
        self.logger.info(self.pid(target_vel))
        return self.check_thresholds(target_vel)

    def check_thresholds(self, cur_velocity):
        if -1 * self.output_threshold < cur_velocity < self.output_threshold:
            return 0

        return cur_velocity

    def error2vel(self, error):
        return error

    def pid(self, target_vel = None):
        if target_vel is not None:
            self.target_vel = target_vel

        error = self.target_vel - self.cur_vel

        self.logger.info(error, target_vel)

        diff_error = error / self.deltaT
        int_error = (error * self.deltaT)

        self.logger.info(diff_error, int_error)

        self.cur_vel = self.cur_vel + self.Kp * error + self.Kd * diff_error + self.Ki * int_error
        self.cur_vel = int(self.cur_vel)

        return self.cur_vel


class ControllerLoop(threading.Thread):
    def __init__(self, threadID, med_dist_queue, lat_dist_queue, logger):
        self.logger = logger

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = MCInterface()

        self.input_filter = InputFilter(logger)

        self.med_dist_queue = med_dist_queue
        self.lat_dist_queue = lat_dist_queue
        self.kill_received = False

    def run(self):
        while not self.kill_received:

            if self.lat_dist_queue.empty():
                self.medial_drive()
            else:
                self.lateral_drive()

            sleep(0.5)

        self.stop()

    def stop(self):
        self.mc.forwardM0(0)
        self.mc.forwardM1(0)

    def set_velocity(self, cur_velocity):
        if cur_velocity > 0:
            self.mc.reverseM0(cur_velocity)
            self.mc.reverseM1(cur_velocity)
        else:
            norm_vel = abs(int(2*cur_velocity))
            self.mc.forwardM0(norm_vel)
            self.mc.forwardM1(norm_vel)

        self.logger.info("Tuned & normalized velocity  " + str(cur_velocity))

    def set_lateral_velocity(self, cur_velocity):
        norm_vel = int(0.7 * cur_velocity)
        if cur_velocity > 0:
            self.mc.forwardM0(norm_vel)
            self.mc.reverseM1(norm_vel)
        else:
            norm_vel = abs(cur_velocity)
            self.mc.reverseM0(norm_vel)
            self.mc.forwardM1(norm_vel)

    def medial_drive(self):
        if self.med_dist_queue.empty():
            self.stop()
            return

        self.logger.debug("Queue: " + str(self.med_dist_queue.queue))
        error = self.med_dist_queue.get()

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.filter(cur_velocity)

        #self.set_velocity(cur_velocity)

    def lateral_drive(self):
        self.logger.debug("Queue: " + str(self.lat_dist_queue.queue))
        error = self.lat_dist_queue.get()

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.filter(cur_velocity)

        #self.set_lateral_velocity(cur_velocity)


