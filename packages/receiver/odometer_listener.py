import threading
import time
from pyee import EventEmitter

from ..common.can_parser import OdometerParser

from .windows_can_receiver import WindowsCANReceiver
from .mock_receiver import MockReceiver
from ..typings import (CanOptions, OdometerOptions)


class OdometerListener(EventEmitter):
    _receiver = None
    _parser = None
    _wheel_speed: float = 0
    _event_time = None
    _received = False

    def __init__(self, can_bus_config: dict, odometer_config: dict, mock: bool = False):
        super(OdometerListener, self).__init__()

        can_options = CanOptions(can_bus_config.get(
            'channel'), int(can_bus_config.get('bitrate')))
        odometer_options = OdometerOptions(odometer_config)

        if mock:
            self._receiver = MockReceiver(odometer_options)
        else:
            self._receiver = WindowsCANReceiver(can_options)

        self._receiver.on('data', self._msg_handler)

        self._parser = OdometerParser(odometer_options)
        self._parser.on('data', self._update_speed_info)

        threading.Thread(target=self._emit_data).start()

    def _emit_data(self):
        while True:
            if self._received:
                self.emit('data', self._event_time, self._wheel_speed)
            time.sleep(0.05)

    def _update_speed_info(self, event_time, speed):
        self._received = True
        self._wheel_speed = speed
        self._event_time = event_time

    def _msg_handler(self, msg):
        if self._parser:
            self._parser.parse(msg)
