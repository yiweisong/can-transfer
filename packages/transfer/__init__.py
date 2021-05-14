from .uart_transfer import UartTransfer
from ..typings import UartOptions


def create_transfer(options: UartOptions) -> UartTransfer:
    try:
        transfer_inst = UartTransfer(options)
    except:
        return None

    return transfer_inst
