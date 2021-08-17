from struct import pack
from packages.common.utils import gps_week_seconds_to_utc
from scapy.all import (Packet, PacketList, sendp, resolve_iface)
from packages.common import utils
from packages.common import uart_helper
# utc_time = gps_week_seconds_to_utc(2166, 463261.918)
# print(utc_time)

if __name__ == '__main__':
    config = utils.get_config()

    iface = resolve_iface(config['local']['name'])  # 'eth0'
    src_mac = config['local']['mac']  # 'b8:27:eb:04:e0:73'
    dst_mac_addresses = config['devices_mac']

    raw_bytes = uart_helper.build_eth_command()

    packet_list = PacketList()
    for i in range(5):
        packet_list.append(
            Packet(raw_bytes)
        )

    sendp(packet_list, iface=iface, verbose=0)
