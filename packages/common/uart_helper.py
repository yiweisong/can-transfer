import struct
from ..typings import UartMessageBody

COMMAND_START = [0x55, 0x55]

def convert_mac_string_to_bytes(mac_str):
    return bytes([int(x, 16) for x in mac_str.split(':')])

def build_command(message_type, message_body: UartMessageBody) -> list:
    payload = transfer_message_body_to_payload(message_body)
    return build_packet(message_type, payload)

def build_eth_command(dest_mac, src_mac, message_type, message_bytes: bytes)->list:
    '''
    Build ethernet packet
    '''
    packet = []
    packet.extend(message_type)
    msg_len = len(message_bytes)

    packet_len = struct.pack("<I", msg_len)

    packet.extend(packet_len)
    final_packet = packet + message_bytes

    msg_len = len(COMMAND_START) + len(final_packet) + 2
    payload_len = struct.pack('>H', len(COMMAND_START) + len(final_packet) + 2)

    whole_packet=[]
    dest = convert_mac_string_to_bytes(dest_mac)
    src = convert_mac_string_to_bytes(src_mac)

    header = dest + src + bytes(payload_len)
    whole_packet.extend(header)

    whole_packet.extend(COMMAND_START)
    whole_packet.extend(final_packet)
    whole_packet.extend(calc_crc(final_packet))
    if msg_len < 46:
        fill_bytes = bytes(46-msg_len)
        whole_packet.extend(fill_bytes)

    return bytes(whole_packet)

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
