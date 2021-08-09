from scapy.all import sendp
from ..typings import EthOptions


class Eth100BaseT1Transfer:
    def __init__(self, options: EthOptions) -> None:
        self._options = options

    def send(self, data):
        sendp(data, iface=self._options.iface, verbose=0)
