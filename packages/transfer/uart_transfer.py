import serial
from ..typings import UartOptions


class UartTransfer:
    serial_port = None

    def __init__(self, options: UartOptions) -> None:
        self.serial_port = serial.Serial(
            port=options.path, baudrate=options.baudrate)
        if not self.serial_port.isOpen():
            self.serial_port.open()

    def send(self, data):
        self.serial_port.write(data)
