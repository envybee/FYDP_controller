from MotorController import MCInterface
import threading
from time import sleep


# Store necessary values to perform sliding window/Kalman filtering and other filtering
class InputFilter:
    def __init__(self):
        # Initialize
        self.prevTime = None

        self.Kp = 1.5
        self.Ki = 0.3
        self.Kd = 0.7

        self.output_threshold = 5

    def filter(self, cur_velocity):
        return self.check_thresholds(cur_velocity)

    def check_thresholds(self, cur_velocity):
	cur_velocity = cur_velocity * 150
        if -1 * self.output_threshold < cur_velocity < self.output_threshold:
            return 0

        return cur_velocity

    def error2vel(self, error):
        return error

    # Not in use currently
    def pid(self, cur_velocity, new_velocity, cur_time, error):

        # Record the time
        if self.prevTime is None:
            self.prevTime = cur_time
            prevError = error
            intError = error
            return

        deltaT = (cur_time - self.prevTime) * 100
        self.prevTime = cur_time

        # error = currVelocity - prevVelocity
        self.logger.info(error, cur_velocity, deltaT)

        # if(abs(error/prevVelocity) > 0.5):
        #   continue

        diffError = (error - self.prevError) / deltaT
        intError = self.prevError + (error * deltaT)
        self.prevError = error

        self.logger.info(diffError, intError)

        cur_velocity = self.Kp * error + self.Kd * diffError + self.Ki * intError
        cur_velocity = int(cur_velocity)

        return cur_velocity


class ControllerLoop(threading.Thread):
    def __init__(self, threadID, med_value, lat_value, logger):
        self.logger = logger

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = MCInterface()

        self.input_filter = InputFilter()

        self.med_value = med_value
        self.lat_value = lat_value
        self.kill_received = False

    def run(self):
        while not self.kill_received:

            if self.med_value != 0:
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

        print("Lateral Drive!!!   --->" + str(cur_velocity))
        norm_vel = int(0.7 * cur_velocity)
        if cur_velocity > 0:
            self.mc.forwardM0(norm_vel)
            self.mc.reverseM1(norm_vel)
        else:
            norm_vel = abs(int(cur_velocity))
            self.mc.reverseM0(norm_vel)
            self.mc.forwardM1(norm_vel)

    def medial_drive(self):
        if self.med_value == 0:
            self.stop()
            return

        self.logger.debug("med_value: " + str(self.med_value))
        error = self.med_value

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.filter(cur_velocity)

        self.set_velocity(cur_velocity)

    def lateral_drive(self):
        self.logger.debug("lat_value: " + str(self.lat_value))
        error = self.lat_value
	#print("Retreived --> " + str(error))

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.filter(cur_velocity)

        self.set_lateral_velocity(cur_velocity)


