def parse_wheel_speed(data):
    '''
    Parse WHEEL_SPEEDS info from Toyota Corolla.
    
    in: CAN msg
    out: in [km/h]
        WHEEL_SPEED_FR
        WHEEL_SPEED_FL
        WHEEL_SPEED_RR
        WHEEL_SPEED_RL
    
    dbc: MSB, unsigned
        BO_ 170 WHEEL_SPEEDS: 8 XXX
        SG_ WHEEL_SPEED_FR : 7|16@0+ (0.01,-67.67) [0|250] "kph" XXX
        SG_ WHEEL_SPEED_FL : 23|16@0+ (0.01,-67.67) [0|250] "kph" XXX
        SG_ WHEEL_SPEED_RR : 39|16@0+ (0.01,-67.67) [0|250] "kph" XXX
        SG_ WHEEL_SPEED_RL : 55
        |16@0+ (0.01,-67.67) [0|250] "kph" XXX
    '''
    offset = -67.67
    speed_fr = (data[0] * 256 + data[1]) * 0.01 + offset
    speed_fl = (data[2] * 256 + data[3]) * 0.01 + offset
    speed_rr = (data[4] * 256 + data[5]) * 0.01 + offset
    speed_rl = (data[6] * 256 + data[7]) * 0.01 + offset
    return (speed_fr, speed_fl, speed_rr, speed_rl)

def parse(message_type, data):
    parse_result = None
    if message_type == 'WHEEL_SPEED':
        parse_result = parse_wheel_speed(data)

    if not parse_result:
        return True, None
    
    return False, parse_result
