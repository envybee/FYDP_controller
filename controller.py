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
    def __init__(self, threadID, med_dist_queue, lat_dist_queue, logger):
        self.logger = logger

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.mc = MCInterface()

        self.input_filter = InputFilter()

        self.med_dist_queue = med_dist_queue
        self.lat_dist_queue = lat_dist_queue
        self.kill_received = False

    def run(self):
        while not self.kill_received:

            if self.lat_dist_queue.empty():
                self.medial_drive()
            else:
                self.lateral_drive()

            sleep(1)

        self.stop()

    def stop(self):
        self.mc.forwardM0(0)
        self.mc.forwardM1(0)

    def set_velocity(self, currVelocity):
        if currVelocity > 0:
            self.mc.reverseM0(currVelocity)
            self.mc.reverseM1(currVelocity)
        else:
            norm_vel = abs(int(2*currVelocity))
            self.mc.forwardM0(norm_vel)
            self.mc.forwardM1(norm_vel)

        self.logger.info("Tuned & normalized velocity  " + str(currVelocity))

    def set_lateral_velocity(self, cur_velocity):
        if cur_velocity > 0:
            self.mc.forwardM0(cur_velocity)
            self.mc.reverseM1(cur_velocity)
        else:
            self.mc.reverseM0(cur_velocity)
            self.mc.forwardM1(cur_velocity)

    def medial_drive(self):
        if self.med_dist_queue.empty():
            self.stop()
            return

        self.logger.debug("Queue: " + str(self.med_dist_queue.queue))
        error = self.med_dist_queue.get()

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.filter(cur_velocity)

        self.set_velocity(cur_velocity)

    def lateral_drive(self):
        self.logger.debug("Queue: " + str(self.lat_dist_queue.queue))
        error = self.lat_dist_queue.get()

        cur_velocity = self.input_filter.error2vel(error)
        cur_velocity = self.input_filter.filter(cur_velocity)

        self.set_lateral_velocity(cur_velocity)


