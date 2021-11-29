from .can_receiver import CANReceiver
from .windows_can_receiver import WindowsCANReceiver
from .uart_receiver import UartReceiver
from .mock_receiver import MockReceiver
from ..typings import (UartOptions, CanOptions)


def create_uart_receiver(options: UartOptions) -> UartReceiver:
    receiver_inst = UartReceiver(options)
    return receiver_inst


def create_can_receiver(options: CanOptions) -> CANReceiver:
    receiver_inst = CANReceiver(options)
    return receiver_inst


def create_windows_receiver(options) -> WindowsCANReceiver:
    receiver_inst = WindowsCANReceiver(options)
    return receiver_inst


def create_mock_receiver(options) -> MockReceiver:
    receiver_inst = MockReceiver(options)
    return receiver_inst
