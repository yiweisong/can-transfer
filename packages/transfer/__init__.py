from .uart_transfer import UartTransfer
from .eth_100base_t1_transfer import Eth100BaseT1Transfer
from ..typings import (UartOptions, EthOptions)


def create_transfer(options: UartOptions) -> UartTransfer:
    try:
        transfer_inst = UartTransfer(options)
    except:
        return None

    return transfer_inst


def create_eth_100base_t1_transfer(options: EthOptions) -> EthOptions:
    try:
        transfer_inst = Eth100BaseT1Transfer(options)
    except:
        return None

    return transfer_inst