
import threading
from bluetooth import *

class Bluetooth(threading.Thread):
    def __init__(self, logger, data):
        self.logger = logger
        self.data = data

        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))
        self.server_sock.listen(1)

        self.kill_received = False

        port = self.server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ef"

        advertise_service(self.server_sock, "SampleServer",
                          service_id=uuid,
                          service_classes=[uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE],
                          #                   protocols = [ OBEX_UUID ]
                          )

        self.logger.info("Waiting for connection on RFCOMM channel %d" % port)

        self.client_sock, client_info = self.server_sock.accept()
        self.logger.info("Accepted connection from " + str(client_info))

    def run(self):
        try:
            while not self.kill_received:
                data = self.client_sock.recv(1024)
                if len(data) == 0: break
                if self.data.upper() == "FALSE":
                    self.data[0] = False
                else:
                    self.data[0] = True

                self.logger.warn("received [%s]" % self.data[0])
        except IOError:
            pass

        self.logger.info("disconnected")

        self.client_sock.close()
        self.server_sock.close()
        self.logger.info("all done")
