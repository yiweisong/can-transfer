import threading
import time
from pyee import EventEmitter

from ..common.can_parser import AbstractParser

from .windows_can_receiver import WindowsCANReceiver
from .mock_receiver import MockReceiver
from ..typings import CanOptions


class OdometerListener(EventEmitter):
    _receiver = None
    _parser = None
    _wheel_speed: float = 0
    _event_time = None
    #_gear: int = 0
    _received = False

    def __init__(self, options: CanOptions, parser: AbstractParser, is_mock: bool = False):
        super(OdometerListener, self).__init__()
        if is_mock:
            self._receiver = MockReceiver({'can_parser': parser.type})
        else:
            self._receiver = WindowsCANReceiver(options)
        self._receiver.on('data', self._msg_handler)

        self._parser = parser
        self._parser.on('data', self._update_speed_info)

        threading.Thread(target=self._emit_data).start()

    def _emit_data(self):
        while True:
            if self._received:
                self.emit('data', self._wheel_speed)
            time.sleep(0.05)

    def _update_speed_info(self, speed):
        self._received = True
        self._wheel_speed = speed

    def _msg_handler(self, msg):
        self._parser.parse(msg)
