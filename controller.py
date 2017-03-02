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

        self.Kp = 0.6
        self.Ki = 0.7
        self.Kd = 0.03

        self.deltaT = 0.1

        self.output_threshold = 5

    def medial_filter(self, target_vel = None):
        self.logger.debug("PID output: " + str(self.pid(target_vel)))

        if target_vel is None:
            return 0

        return self.check_thresholds(target_vel)

    def lateral_filter(self, target_vel):
        return self.check_thresholds(target_vel)

    def check_thresholds(self, cur_velocity):
        if -1 * self.output_threshold < cur_velocity < self.output_threshold:
            return 0

        return cur_velocity

    def error2vel(self, error):
        return error

    def error2vel_vision(self, error):
        cur_velocity = error * 100
        return cur_velocity

    def pid(self, target_vel = None):
        if target_vel is not None:
            self.target_vel = target_vel

        error = self.target_vel - self.cur_vel

        self.logger.debug("Error: " + str(error) + ", Target Value: " + str(target_vel))

        diff_error = error / self.deltaT
        int_error = (error * self.deltaT)

        self.logger.debug("Diff Error: " + str(diff_error) + ", Int Error: " + str(int_error))

        self.cur_vel = self.cur_vel + self.Kp * error + self.Kd * diff_error + self.Ki * int_error
        self.cur_vel = int(self.cur_vel)

        return self.cur_vel


class ControllerLoop(threading.Thread):
    def __init__(self, threadID, med_value, lat_value, logger):
        self.logger = logger

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = MCInterface()

        self.input_filter = InputFilter(logger)

        self.med_value = med_value
        self.lat_value = lat_value
        self.kill_received = False

    def run(self):
        while not self.kill_received:

            if self.lat_value[0] == 0:
                self.medial_drive()
            else:
                self.lateral_drive()

            sleep(0.01)

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

        self.logger.debug("Tuned & normalized velocity  " + str(cur_velocity))

    def set_lateral_velocity(self, cur_velocity):

        self.logger.debug("Lateral Drive!!!   --->" + str(cur_velocity))
        norm_vel = int(cur_velocity)
        if cur_velocity > 0:
            for s in range(10, 15):
                self.mc.forwardM0(15 + norm_vel)
                self.mc.reverseM1(15)
        else:
            for s in range(10, 15):
                norm_vel = abs(int(cur_velocity))
                self.mc.reverseM0(15)
                self.mc.forwardM1(15 + norm_vel)

    def medial_drive(self):
        self.logger.debug("Received med_value: " + str(self.med_value))
        error = self.med_value[0]

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.medial_filter(cur_velocity)

        self.logger.debug("cur_velocity: " + str(cur_velocity))

        self.set_velocity(cur_velocity)

    def lateral_drive(self):
        error = self.lat_value[0]

        self.logger.debug("Received lat_value: " + str(error))
        cur_velocity = self.input_filter.error2vel_vision(error)
        cur_velocity = self.input_filter.lateral_filter(cur_velocity)

        self.set_lateral_velocity(cur_velocity)


