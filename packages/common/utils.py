import os
import sys
import json
import struct
from datetime import datetime, timedelta
from functools import wraps

IS_WINDOWS = sys.platform.__contains__('win32') or sys.platform.__contains__('win64')

# 闰秒
LEAP_SECONDS = 18

# 输入：GPS周、GPS周内秒、闰秒（可选，gps时间不同，闰秒值也不同，由Leap_Second.dat文件决定）
# 输出：UTC时间（格林尼治时间）
# 输入示例： gps_week_seconds_to_utc(2119, 214365.000)
# 输出示例： '2020-08-18 11:32:27.000000'
def gps_week_seconds_to_utc(gpsweek, gpsseconds, leapseconds=LEAP_SECONDS):
    datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
    epoch = datetime.strptime("1980-01-06 00:00:00.000", datetimeformat)
    # timedelta函数会处理seconds为负数的情况
    elapsed = timedelta(days=(gpsweek*7), seconds=(gpsseconds-leapseconds))
    return datetime.strftime(epoch+elapsed, datetimeformat)

def get_config():
    conf = {}
    with open(os.path.join(os.getcwd(), 'config.json')) as json_data:
        conf = (json.load(json_data))
    return conf

def print_message(msg, *args):
    format_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print('{0} - {1}'.format(format_time, msg), *args)

def convert_mac_to_sn(mac_address: str):
    str_sn_parts = mac_address.split(':')[0:4]
    integer_sn_parts = [int(value, 16) for value in str_sn_parts]
    return struct.unpack('<I', bytes(integer_sn_parts))[0]

def throttle(seconds=0, minutes=0, hours=0):
    throttle_period = timedelta(seconds=seconds, minutes=minutes, hours=hours)

    def throttle_decorator(fn):
        time_of_last_call = datetime.min

        @wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal time_of_last_call
            now = datetime.now()
            if now - time_of_last_call > throttle_period:
                time_of_last_call = now
                return fn(*args, **kwargs)
        return wrapper
    return throttle_decorator

def platform_setup(func):
    '''
    do some prepare work for different platform
    '''
    if IS_WINDOWS:
        from .platform import win
        win.disable_console_quick_edit_mode()
    
    @wraps(func)
    def decorated(*args, **kwargs):
        func(*args, **kwargs)
    return decorated