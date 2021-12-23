import time
from typing import List
from scapy.all import (Packet, AsyncSniffer, sendp)
from ..typings import EthernetDevice
from ..common import uart_helper

PING_PKT = b'\x01\xcc'

global PING_RESULT

PING_RESULT = {}


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

    command_line = uart_helper.build_eth_command(
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
