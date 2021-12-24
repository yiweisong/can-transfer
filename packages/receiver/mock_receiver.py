import time
import threading
import random
from pyee import EventEmitter


class mock_can_message:
    arbitration_id = 0
    data = []
    timestamp = 0


def mock_speed_message(can_parser_type):
    speed_data = []
    for _ in range(8):
        speed_data.append(random.randint(1, 255))

    msg = mock_can_message()
    if can_parser_type == 'DefaultParser':
        msg.arbitration_id = 0xAA
    elif can_parser_type == 'Customer1Parser':
        msg.arbitration_id = 0xB6
    elif can_parser_type == 'Customer2Parser':
        msg.arbitration_id = 0x98fe6e0b
    else:
        msg.arbitration_id = 0xAA

    msg.timestamp = time.time()
    msg.data = speed_data
    return msg


class MockReceiver(EventEmitter):
    def __init__(self, options):
        super(MockReceiver, self).__init__()
        can_parser_type = options['can_parser']
        threading.Thread(target=self._receive, args=(can_parser_type,)).start()

    def _receive(self, can_parser_type):
        frequency = 20/1000
        while True:
            message = mock_speed_message(can_parser_type)
            self.emit('data', message)
            time.sleep(frequency)
