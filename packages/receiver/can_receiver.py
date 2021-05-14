import os

import sys
import math
import time
import datetime
import can
import threading
import time
from pyee import EventEmitter
from ..typings import CanOptions


class CANReceiver(EventEmitter):
    def __init__(self, options: CanOptions) -> None:
        super(CANReceiver, self).__init__()

        # close can0
        os.system('sudo ifconfig {0} down'.format(options.channel))
        # set bitrate of can0
        os.system('sudo ip link set {0} type can bitrate {1}'.format(
            options.channel, options.bitrate))
        # open can0
        os.system('sudo ifconfig {0} up'.format(options.channel))
        # os.system('sudo /sbin/ip link set can0 up type can bitrate 250000')
        # show details can0 for debug.
        # os.system('sudo ip -details link show can0')

        # set up can interface.
        # socketcan_native socketcan_ctypes
        self.can0 = can.interface.Bus(
            channel=options.channel, bustype='socketcan_ctypes')
        # set up Notifier
        self.notifier = can.Notifier(self.can0, [self.msg_handler])

    def msg_handler(self, msg):
        self.emit('data', msg)
