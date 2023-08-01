import os
import time
import threading
from unittest import mock
from packages.receiver.odometer_listener import OdometerListener
from packages.transfer import (create_transfer, create_eth_100base_t1_transfer)
from packages.transfer.transfer_center import TransferCenter
from packages.common import (utils, app_logger)


print_message = utils.print_message


def read_config():
    config = utils.get_config()
    return config


def transfer_task():
    # read configuration, generate transfers
    config = read_config()

    transfer_center = TransferCenter(config['can_transfer'])

    last_error = transfer_center.get_error()
    if last_error:
        print_message('[Error] Initalize transfer center failed.')
        print_message('[Error] {0}'.format(last_error.message))

        if transfer_center.can_continue_work:
            print_message('[Info] Although some transfer failed to initialize, but the others are ready')
        else:
            print_message('[Error] No transfer is ready, exit.')
            return
    

    can_speed_log = app_logger.create_logger('can_speed')


    def handle_wheel_speed_data(event_time, speed):
        try:
            transfer_center.dispatch_vehicle_speed(speed)
        except Exception as ex:
            print_message('[Error] Dispatch data has error')
            print_message('[Error] Reason:{0}'.format(ex))
            #trace_log.append('[Error] Reason:{0}'.format(ex))
        # log timestamp
        can_speed_log.append('{0}, {1}'.format(event_time, speed))

    try:
        print_message('[Info] Transfer center is starting...')
        odometer_listener = OdometerListener(
            config['can_bus'], config['odometer'])
        odometer_listener.on('data', handle_wheel_speed_data)
    except Exception as ex:
        print_message('[Error] Odometer listener has error')
        print_message('[Error] Reason:{0}'.format(ex))


@utils.platform_setup
def start_task():
    app_logger.new_session()
    print_message('[Info] Application start working...')
    threading.Thread(target=transfer_task).start()


if __name__ == '__main__':
    try:
        start_task()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        os._exit(1)
