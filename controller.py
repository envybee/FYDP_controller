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
        self.Ki = 0
        self.Kd = 0

        self.deltaT = 0.1

        self.output_threshold = 15

    def medial_filter(self, target_vel = None):
        pid_value = self.pid(target_vel)
        self.logger.info("PID output: " + str(pid_value))

        if target_vel is None:
            return 0

        return self.check_thresholds(pid_value)

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
    def __init__(self, threadID, med_value, lat_value, logger, bt_signal):
        self.logger = logger

        self.bt_signal = bt_signal

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = MCInterface()

        self.input_filter = InputFilter(logger)

        self.med_value = med_value
        self.lat_value = lat_value
        self.kill_received = False

    def run(self):
        while not self.kill_received and self.bt_signal[0]:

            if self.lat_value[0] == 0:
                self.medial_drive()
            else:
                self.lateral_drive()

            sleep(0.01)

        self.stop()

        if not self.kill_received:
            self.logger.info("Paused")
            sleep(0.1)
            self.run()

    def stop(self):
        self.mc.forwardM0(0)
        self.mc.forwardM1(0)

    def set_velocity(self, cur_velocity):
        if cur_velocity > 0:
            self.mc.forwardM0(cur_velocity)
            self.mc.reverseM1(cur_velocity)
        else:
            norm_vel = abs(cur_velocity)
            self.mc.reverseM0(norm_vel)
            self.mc.forwardM1(norm_vel)

        self.logger.debug("Tuned & normalized velocity  " + str(cur_velocity))

    def set_lateral_velocity(self, cur_velocity):

        self.logger.debug("Lateral Drive!!!   --->" + str(cur_velocity))
        norm_vel = int(cur_velocity)
        if cur_velocity > 0:
            for s in range(10, 15):
                self.mc.reverseM0(15 + norm_vel)
                self.mc.reverseM1(15)
        else:
            for s in range(10, 15):
                norm_vel = abs(int(cur_velocity))
                self.mc.forwardM0(15)
                self.mc.forwardM1(15 + norm_vel)

    def medial_drive(self):
        self.logger.info("Received med_value: " + str(self.med_value))
        error = self.med_value[0]

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.medial_filter(cur_velocity)
 
        self.logger.info("cur_velocity: " + str(cur_velocity))

        self.input_filter.cur_vel = cur_velocity
        
        if cur_velocity > 0 and cur_velocity < 100: 
              self.set_velocity(60)
        elif cur_velocity > 100 and cur_velocity < 200:
            for s in range(100, cur_velocity, 10): 
              self.set_velocity(s)
        elif cur_velocity > 100 and cur_velocity < 200:
            for s in range(100, cur_velocity, 20): 
              self.set_velocity(s)
        else:
            self.set_velocity(0)
        #self.set_velocity(cur_velocity)

    def lateral_drive(self):
        error = self.lat_value[0]

        self.logger.debug("Received lat_value: " + str(error))
        cur_velocity = self.input_filter.error2vel_vision(error)
        cur_velocity = self.input_filter.lateral_filter(cur_velocity)

        self.set_lateral_velocity(cur_velocity)


