
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
            self.logger.info("Received: " + data)
            self.populate_queue(data)

    def get_data(self):
        inp = input()
        return inp

    def populate_queue(self, data):
        self.data_queue.put(data)

    def normalize(self):
        pass