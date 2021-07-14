import time
import threading
import random
from pyee import EventEmitter


class mock_can_message:
    arbitration_id = 0
    data = []
    timestamp = 0


def mock_speed_message():
    speed_data = []
    for _ in range(8):
        speed_data.append(random.randint(1, 255))

    msg = mock_can_message()
    msg.arbitration_id = 0xAA
    msg.timestamp = time.time()
    msg.data = speed_data
    return msg


class MockReceiver(EventEmitter):
    def __init__(self):
        super(MockReceiver, self).__init__()
        threading.Thread(target=self._receive).start()

    def _receive(self):
        while True:
            message = mock_speed_message()
            self.emit('data', message)
            time.sleep(0.1)
