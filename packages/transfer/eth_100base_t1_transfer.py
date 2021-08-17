from scapy.all import (sendp, Packet, PacketList)
from ..typings import EthOptions
from datetime import datetime


class Eth100BaseT1Transfer:
    def __init__(self, options: EthOptions) -> None:
        self._options = options

    def send(self, data):
        sendp(data, iface=self._options.iface, verbose=0)

    def send_batch(self, batches):
        packets_len = len(batches)
        if packets_len == 0:
            return

        packet_list = PacketList()
        for pkt in batches:
            packet_raw = Packet(pkt)
            packet_list.append(packet_raw)

        sendp(packet_list, iface=self._options.iface, verbose=0)
