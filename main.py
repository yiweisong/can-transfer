import os
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
from packages.transfer.transfer_center import TransferCenter
from packages.typings import (
    UartOptions, CanOptions, UartMessageBody, EthOptions)
from packages.common import (utils, app_logger)
from packages.common.can_parser import CanParserFactory


print_message = utils.print_message


def read_config():
    config = utils.get_config()
    if not config.__contains__('can_parser'):
        config['can_parser'] = 'DefaultParser'
    return config


def transfer_task():
    # read configuration, generate transfers
    config = read_config()
    transfer_center = TransferCenter(config['can_transfer'])

    last_error = transfer_center.get_error()
    if last_error:
        print_message(
            '[Error] Initalize transfer failed.')
        print_message('[Error]', last_error.message)
        return

    # parse can message
    can_parser = CanParserFactory.create(config['can_parser'])
    can_speed_log = app_logger.create_logger('can_speed')

    @utils.throttle(seconds=0.05)
    def handle_wheel_speed_data(data):
        # parse wheel speed
        parse_error, parse_result = can_parser.parse('WHEEL_SPEED', data.data)
        if parse_error:
            return

        speed = parse_result

        # dispatch to transfers
        transfer_center.dispatch_vehicle_speed(speed)

        # log timestamp
        can_speed_log.append('{0}, {1}'.format(data.timestamp, speed))

    def receiver_handler(data):
        if can_parser.need_handle_speed_data(data.arbitration_id):
            handle_wheel_speed_data(data)

    try:
        print_message('[Info] Transfer task started')
        # can_log_receiver = create_mock_receiver(
        #     {'can_parser': config['can_parser']})
        can_log_receiver = create_windows_receiver(CanOptions(0, 500000))
        can_log_receiver.on('data', receiver_handler)
    except Exception as ex:
        print_message('[Error] Transfer task has error')
        print_message('[Error] Reason:{0}'.format(ex))


def start_task():
    app_logger.new_session()
    threading.Thread(target=transfer_task).start()


if __name__ == '__main__':
    try:
        # iface = select_ethernet_interface()
        print_message('[Info] Application start working...')
        start_task()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        os._exit(1)
