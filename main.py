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
from packages.typings import (
    UartOptions, CanOptions, UartMessageBody, EthOptions)
from packages.common import (uart_helper, utils, app_logger)
from packages.common.can_parser import CanParserFactory
from packages.other import novatel_logger
from packages.devices.eth_device import collect_devices
from terminal_layout import *
from terminal_layout.extensions.choice import *

print_message = utils.print_message


def select_ethernet_interface():
    '''
     load local network interface from config.json
     if set use the configured one, else scan the network interfaces
    '''
    from scapy.all import conf, resolve_iface
    app_conf = utils.get_config()
    config_file_path = os.path.join(os.getcwd(), 'config.json')

    if app_conf.__contains__('local'):
        return resolve_iface(app_conf['local']['name'])

    ethernet_list = [conf.ifaces[item].name for item in conf.ifaces]
    c = Choice('Which ehternet interface you are using?',
               ethernet_list,
               icon_style=StringStyle(fore=Fore.green),
               selected_style=StringStyle(fore=Fore.green), default_index=0)

    choice = c.get_choice()
    if choice:
        index, value = choice
        # save to config.json

        network_interface = resolve_iface(value)
        app_conf['local'] = {
            'name': network_interface.description,
            'mac': network_interface.mac
        }
        try:
            with open(config_file_path, 'w') as outfile:
                json.dump(app_conf, outfile, indent=4, ensure_ascii=False)
            return network_interface
        except:
            print('Write configuration failed')
            return None

    return None


def build_eth_commands(devices_mac, local_mac, packet_type_bytes, message_bytes):
    commands = []
    for dest_mac in devices_mac:
        command = uart_helper.build_eth_command(dest_mac, local_mac,
                                                packet_type_bytes,
                                                message_bytes)
        commands.append(command)

    return commands


def output_device_mac_addresses(mac_addresses):
    print('[Info] Listen mac address list:')
    if len(mac_addresses) == 0:
        print('[Info] No device detected')

    for address in mac_addresses:
        print('MAC: {0}, SN: {1}'.format(
            address, utils.convert_mac_to_sn(address)))


def can_log_task():
    from scapy.all import resolve_iface
    can_speed_log = app_logger.create_logger('can_speed')

    config = utils.get_config()
    if not config.__contains__('can_parser'):
        config['can_parser'] = 'DefaultParser'

    iface = resolve_iface(config['local']['name'])  # 'eth0'
    src_mac = config['local']['mac']  # 'b8:27:eb:04:e0:73'

    eth_devices = collect_devices(iface, src_mac)

    if not config.get('devices_mac') or len(config['devices_mac']) == 0:
        dst_mac_addresses = [device.mac_address for device in eth_devices]
    else:
        dst_mac_addresses = config['devices_mac']

    output_device_mac_addresses(dst_mac_addresses)

    can_log_transfer = create_eth_100base_t1_transfer(
        EthOptions(iface, src_mac, dst_mac_addresses))

    can_parser = CanParserFactory.create(config['can_parser'])

    def build_speed(speed_data) -> float:
        avg_speed = (speed_data[2]+speed_data[3])/2
        return avg_speed

    @utils.throttle(seconds=0.05)
    def handle_wheel_speed_data(data):
        # parse wheel speed
        parse_error, parse_result = can_parser.parse('WHEEL_SPEED', data.data)
        if parse_error:
            return

        speed = build_speed(parse_result)

        # append_to_speed_queue(speed)
        commands = build_eth_commands(dst_mac_addresses, src_mac,
                                      bytes([0x01, 0x0b]),
                                      list(struct.pack("<f", speed)))

        if can_log_transfer:
            can_log_transfer.send_batch(commands)

        # log timestamp
        can_speed_log.append('{0}, {1}'.format(data.timestamp, speed))

    def receiver_handler(data):
        if can_parser.need_handle_speed_data(data.arbitration_id):
            handle_wheel_speed_data(data)

    try:
        print_message('[Info] CAN log task started')
        #can_log_receiver = create_mock_receiver({'can_parser': config['can_parser']})
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


def mock_speed_task():
    import random
    from scapy.all import resolve_iface
    can_speed_log = app_logger.create_logger('can_speed')
    config = utils.get_config()

    iface = resolve_iface(config['local']['name'])  # 'eth0'
    src_mac = config['local']['mac']  # 'b8:27:eb:04:e0:73'

    eth_devices = collect_devices(iface, src_mac)

    if not config.get('devices_mac') or len(config['devices_mac']) == 0:
        dst_mac_addresses = [device.mac_address for device in eth_devices]
    else:
        dst_mac_addresses = config['devices_mac']

    eth_transfer = create_eth_100base_t1_transfer(
        EthOptions(iface, src_mac, dst_mac_addresses))

    @utils.throttle(seconds=0.05)
    def send_speed_data():
        speed = random.randint(1, 255)

        # append_to_speed_queue(speed)
        commands = build_eth_commands(dst_mac_addresses, src_mac, bytes(
            [0x01, 0x0b]), list(struct.pack("<f", speed)))

        if eth_transfer:
            eth_transfer.send_batch(commands)

        # log timestamp
        can_speed_log.append('{0}'.format(speed))

    while True:
        send_speed_data()
        time.sleep(0.01)


def start_task():
    app_logger.new_session()
    threading.Thread(target=can_log_task).start()
    # threading.Thread(target=transfer_task).start()
    # threading.Thread(target=novatel_log_task).start()
    # threading.Thread(target=mock_speed_task).start()


if __name__ == '__main__':
    try:
        iface = select_ethernet_interface()
        start_task()

        print_message('[Info] Application start working...')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        os._exit(1)
