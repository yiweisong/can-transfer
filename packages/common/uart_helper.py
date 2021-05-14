import struct
from ..typings import UartMessageBody

COMMAND_START = [0x55, 0x55]


def build_command(message_type, message_body: UartMessageBody) -> list:
    payload = transfer_message_body_to_payload(message_body)
    return build_packet(message_type, payload)


def transfer_message_body_to_payload(message_body: UartMessageBody) -> list:
    if message_body.type == 'float':
        return list(struct.unpack("4B", struct.pack("<f", message_body.data)))
    return []


def build_packet(message_type, message_bytes=[]) -> list:
    '''
    Build final packet
    '''
    packet = []
    packet.extend(bytearray(message_type, 'utf-8'))

    msg_len = len(message_bytes)
    packet.append(msg_len)
    final_packet = packet + message_bytes

    return COMMAND_START + final_packet + calc_crc(final_packet)


def calc_crc(payload):
    '''
    Calculates 16-bit CRC-CCITT
    '''
    crc = 0x1D0F
    for bytedata in payload:
        crc = crc ^ (bytedata << 8)
        i = 0
        while i < 8:
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            i += 1

    crc = crc & 0xffff
    crc_msb = (crc & 0xFF00) >> 8
    crc_lsb = (crc & 0x00FF)
    return [crc_msb, crc_lsb]
