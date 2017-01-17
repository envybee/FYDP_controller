
import threading

class Inputs(threading.Thread):
    def __init__(self, data_queue, threadID):
        self.data_queue = data_queue
        self.establish_connection()

        threading.Thread.__init__(self)
        self.threadID = threadID

    def establish_connection(self):
        pass

    def run(self):
        while True:
            data = self.get_data()
            if data != "trash":
                self.populate_queue(data)

    def populate_queue(self):
        pass

    def normalize(self):
        pass