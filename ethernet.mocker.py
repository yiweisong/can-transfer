import struct
from packages.common import (uart_helper)

DST_MAC = '01:02:03:04:05:06'
SRC_MAC = '06:05:04:03:02:01'


def mock_speed(speed: int):
    message_bytes = list(struct.pack("<f", speed))
    command = uart_helper.build_eth_command(DST_MAC, SRC_MAC,
                                            bytes([0x01, 0x0b]),
                                            message_bytes)
    print(' '.join(['{:0>2x}'.format(x) for x in command]))


if __name__ == '__main__':
    mock_speed(20)
    mock_speed(-2)
