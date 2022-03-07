import os
import time
import json
from typing import List
from scapy.all import (Packet, AsyncSniffer, sendp)
from ..typings import EthernetDevice
from ..common import (message_helper,utils)
from terminal_layout import *
from terminal_layout.extensions.choice import *

PING_PKT = b'\x01\xcc'

global PING_RESULT

PING_RESULT = {}

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

def convert_bytes_to_string(bytes_data, link=''):
    return link.join(['%02x' % b for b in bytes_data])


def handle_ping_receive_packet(data: Packet):
    raw_data = bytes(data)
    src = raw_data[6:12]
    device_mac = convert_bytes_to_string(src, ':')

    PING_RESULT[device_mac] = raw_data


def collect_devices(iface, src_mac, timeout=5) -> List[EthernetDevice]:
    global PING_RESULT
    PING_RESULT = {}
    devices = []
    filter_exp = 'ether dst host {0} and ether[16:2] == 0x01cc'.format(
        src_mac)

    command_line = message_helper.build_eth_command(
        dest_mac="ff:ff:ff:ff:ff:ff",
        src_mac=src_mac,
        message_type=PING_PKT,
        message_bytes=[]
    )

    async_sniffer = AsyncSniffer(
        iface=iface,
        prn=handle_ping_receive_packet,
        filter=filter_exp
    )

    async_sniffer.start()
    time.sleep(.1)
    sendp(command_line, iface=iface, verbose=0, count=1)
    time.sleep(timeout)
    async_sniffer.stop()

    for key in PING_RESULT.keys():
        devices.append(EthernetDevice(key))

    return devices
