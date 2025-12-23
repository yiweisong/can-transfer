import os
import can
from pyee import EventEmitter
from ..typings import CanOptions
from ..common.context import AppContext

class WindowsCANReceiver(EventEmitter):
    def __init__(self, options: CanOptions) -> None:
        super(WindowsCANReceiver, self).__init__()

        if AppContext.can_bus is None:
            AppContext.can_bus = can.interface.Bus(
                channel=options.channel, 
                bustype='canalystii', 
                bitrate=options.bitrate
            )
        self.can = AppContext.can_bus
        # set up Notifier
        simple_listener = SimpleListener(self)
        self.notifier = can.Notifier(self.can, [simple_listener])


class SimpleListener(can.Listener):
    _receiver = None

    def __init__(self, receiver: WindowsCANReceiver) -> None:
        super().__init__()
        self._receiver = receiver

    def on_message_received(self, msg):
        self._receiver.emit('data', msg)

    def on_error(self, exc):
        print(exc)
