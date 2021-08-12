import os
import can
import time
import random
from pyee import EventEmitter
from ..typings import CanOptions


def mock_speed_message():
    speed_data = []
    for _ in range(8):
        speed_data.append(random.randint(1, 255))

    return speed_data


class CARMocker(EventEmitter):
    def __init__(self, options: CanOptions) -> None:
        super(CARMocker, self).__init__()

        # close can0
        os.system('sudo ifconfig {0} down'.format(options.channel))
        # set bitrate of can0
        os.system('sudo ip link set {0} type can bitrate {1}'.format(
            options.channel, options.bitrate))
        # os.system(
        #     'sudo ip link set {0} type can restart-ms 100'.format(options.channel))
        # open can0
        os.system('sudo ifconfig {0} up'.format(options.channel))

        # os.system('sudo /sbin/ip link set can0 up type can bitrate 250000')
        # show details can0 for debug.
        # os.system('sudo ip -details link show can0')

        # set up can interface.
        # socketcan_native socketcan_ctypes
        self.can0 = can.interface.Bus(
            channel=options.channel, bustype='socketcan_ctypes')

    def gen_random_speed(self):
        msg_id = 0x000000AA
        speed = mock_speed_message()
        msg = can.Message(arbitration_id=msg_id,
                            data=speed, extended_id=True)
        self.can0.send(msg)
