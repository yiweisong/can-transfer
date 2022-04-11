from struct import pack
from packages.common.utils import gps_week_seconds_to_utc
from scapy.all import (Packet, PacketList, sendp, resolve_iface)
from packages.common import utils
from packages.common import message_helper
# utc_time = gps_week_seconds_to_utc(2166, 463261.918)
# print(utc_time)

if __name__ == '__main__':
    msg1 = message_helper.build_nmea_message(['PQTMCFGDRMODE','0'])
    print(msg1)

    # msg2 = message_helper.build_nmea_message(['PQTMCFGDRMODE','1','2'])
    # print(msg2)

    print(message_helper.build_nmea_message(['PQTMVEHMSG','1','0',str(0)]))
    print(message_helper.build_nmea_message(['PQTMVEHMSG','1','0',str(12.3)]))
    print(message_helper.build_nmea_message(['PQTMVEHMSG','1','0',str(20.5)]))
    print(message_helper.build_nmea_message(['PQTMVEHMSG','1','0',str(30.8)]))
    #print(msg3)
