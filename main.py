import time
import threading
import struct
import json
from datetime import datetime
from packages.receiver import (
    create_uart_receiver,
    create_can_receiver,
    create_mock_receiver,
    create_windows_receiver
)
from packages.transfer import (create_transfer, create_eth_100base_t1_transfer)
from packages.typings import (
    UartOptions, CanOptions, UartMessageBody, EthOptions)
from packages.common import (can_parser, uart_helper, utils, app_logger)
from packages.other import novatel_logger

print_message = utils.print_message


def build_eth_commands(devices_mac, local_mac, packet_type_bytes, message_bytes):
    commands = []
    for dest_mac in devices_mac:
        command = uart_helper.build_eth_command(dest_mac, local_mac,
                                                packet_type_bytes,
                                                message_bytes)
        commands.append(command)

    return commands


def can_log_task():
    can_speed_log = app_logger.create_logger('can_speed')
    config = utils.get_config()

    iface = config['local']['name']  # 'eth0'
    src_mac = config['local']['mac']  # 'b8:27:eb:04:e0:73'
    dst_mac_addresses = config['devices_mac']

    can_log_transfer = create_eth_100base_t1_transfer(
        EthOptions(iface, src_mac, dst_mac_addresses))

    def build_speed(speed_data) -> float:
        avg_speed = (speed_data[2]+speed_data[3])/2
        return avg_speed  # * 1000/1000

    def handle_wheel_speed_data(data):
        # parse wheel speed
        parse_error, parse_result = can_parser.parse('WHEEL_SPEED', data.data)
        if parse_error:
            return

        speed = build_speed(parse_result)
        # build message for serial port
        # command = uart_helper.build_command(
        #     'cA', UartMessageBody('float', speed))

        # append_to_speed_queue(speed)
        commands = build_eth_commands(dst_mac_addresses, src_mac,
                                      bytes([0x01, 0x0b]),
                                      list(struct.pack("<f", speed)))

        if can_log_transfer:
            for command in commands:
                can_log_transfer.send(command)

        # log timestamp
        can_speed_log.append('{0}, {1}'.format(data.timestamp, speed))

    @utils.throttle(seconds=0.05)
    def receiver_handler(data):
        # parse message id 0xAA(170), it stands for wheel speed
        if data.arbitration_id == 0xAA:
            handle_wheel_speed_data(data)

    try:
        print_message('[Info] CAN log task started')
        # create_transfer(UartOptions('/dev/ttyUSB0', 460800))
        # create_mock_receiver()
        can_log_receiver = create_windows_receiver(CanOptions(0, 500000))
        can_log_receiver.on('data', receiver_handler)
    except Exception as ex:
        print_message('[Error] CAN log task has error')
        print_message('[Error] Reason:{0}'.format(ex))


def novatel_log_task():
    try:
        print_message('[Info] Novatel log task started')
        novatel_logger.start(UartOptions('/dev/ttyUSB0', 230400))
    except Exception as ex:
        print_message('[Error] Novatel log task has error')
        print_message('[Error] Reason:{0}'.format(ex))
    # TODO: refactor as receiver
    # def receiver_handler(data):
    #     pass

    # novatel_log_receiver = create_novatel_receiver()
    # novatel_log_receiver.on('data', receiver_handler)


if __name__ == '__main__':
    app_logger.new_session()

    threading.Thread(target=can_log_task).start()
    # threading.Thread(target=transfer_task).start()
    # threading.Thread(target=novatel_log_task).start()

    print_message('[Info] Application start working...')
    while True:
        time.sleep(1)
        print_message('heartbeat...')
