import time
import threading
import serial
from ..typings import UartOptions
from pyee import EventEmitter


class UartReceiver(EventEmitter):
    serial_port = None

    def __init__(self, options: UartOptions) -> None:
        super(UartReceiver, self).__init__()

        self.serial_port = serial.Serial(
            port=options.path, baudrate=options.baudrate)
        #self.serial_port.open()

        threading.Thread(target=self._receive).start()

    def _receive(self):
        while True:
            received_data = self.serial_port.read(100)
            self.emit('data', received_data)
            time.sleep(0.1)
