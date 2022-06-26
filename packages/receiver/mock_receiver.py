import time
import threading
import random
from pyee import EventEmitter

from ..typings import (OdometerOptions, SignalOptions)


class mock_can_message:
    arbitration_id = 0
    data = []
    timestamp = 0


def mock_speed_message(speed_options:SignalOptions):
    speed_data = []
    for _ in range(8):
        speed_data.append(random.randint(0, 255))

    msg = mock_can_message()
    
    msg.arbitration_id = speed_options.id

    msg.timestamp = time.time()
    msg.data = bytes(speed_data)
    return msg


def mock_gear_message(gear_options:SignalOptions):
    gear_data = []
    for _ in range(8):
        gear_data.append(random.randint(0, 32))

    msg = mock_can_message()

    msg.arbitration_id = gear_options.id

    msg.timestamp = time.time()
    msg.data = bytes(gear_data)
    return msg


class MockReceiver(EventEmitter):
    def __init__(self, options: OdometerOptions):
        super(MockReceiver, self).__init__()
        threading.Thread(target=self._receive, args=(options,)).start()

    def _receive(self, options: OdometerOptions):
        frequency = 20/1000
        while True:
            if options.speed:
                message = mock_speed_message(options.speed)
                self.emit('data', message)

            if options.gear:
                message = mock_gear_message(options.gear)
                self.emit('data', message)
            time.sleep(frequency)
