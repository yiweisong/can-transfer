from os import spawnlp
import time

from packages.receiver import (
    create_uart_receiver,
    create_can_receiver,
    create_mock_receiver
)
from packages.transfer import create_transfer
from packages.typings import (UartOptions, CanOptions, UartMessageBody)
from packages.common import (can_parser, uart_helper, log_helper)


def build_speed(speed_data) -> float:
    avg_speed = (speed_data[2]+speed_data[3])/2
    return avg_speed / 3600  # * 1000/1000


def handle_wheel_speed_data(data):
    # parse wheel speed
    parse_error, parse_result = can_parser.parse('WHEEL_SPEED', data.data)
    if parse_error:
        return

    speed = build_speed(parse_result)
    # build message for serial port
    command = uart_helper.build_command('cA', UartMessageBody('float', speed))

    if TRANSFER:
        TRANSFER.send(command)
    log_helper.log_speed(speed)


def receiver_handler(data):
    # parse message id 0xAA(170), it stands for wheel speed
    if data.arbitration_id == 0xAA:
        handle_wheel_speed_data(data)


TRANSFER = create_transfer(UartOptions('/dev/ttyUSB0', 460800))
# create_mock_receiver()
RECEIVER = create_can_receiver(CanOptions('can0', 500000))
# create_transfer(UartOptions('/dev/cu.usbserial-AK005M29', 460800))
RECEIVER.on('data', receiver_handler)

while 1:
    time.sleep(1)
