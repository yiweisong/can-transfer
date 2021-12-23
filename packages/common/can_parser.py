from abc import ABCMeta, abstractmethod


class AbstractParser:
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, message_type, data):
        '''
        parse message
        '''

    def need_handle_speed_data(self, arbitration_id) -> bool:
        '''
        check if the arbitration_id contains speed info
        '''


class DefaultParser(AbstractParser):
    def __init__(self):
        super(DefaultParser, self).__init__()
        pass

    def need_handle_speed_data(self, arbitration_id):
        return arbitration_id == 0xAA

    def parse(self, message_type, data):
        parse_result = None
        if message_type == 'WHEEL_SPEED':
            parse_result = self.parse_wheel_speed(data)

        if not parse_result:
            return True, None

        return False, parse_result

    def parse_wheel_speed(self, data):
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
        scale = 0.01
        speed_fr = (data[0] * 256 + data[1]) * scale + offset
        speed_fl = (data[2] * 256 + data[3]) * scale + offset
        speed_rr = (data[4] * 256 + data[5]) * scale + offset
        speed_rl = (data[6] * 256 + data[7]) * scale + offset
        return (speed_fr, speed_fl, speed_rr, speed_rl)


class Customer1Parser(AbstractParser):
    def __init__(self):
        super(Customer1Parser, self).__init__()

    def need_handle_speed_data(self, arbitration_id):
        return arbitration_id == 0xB6

    def parse(self, message_type, data):
        parse_result = None
        if message_type == 'WHEEL_SPEED':
            parse_result = self.parse_wheel_speed(data)

        if not parse_result:
            return True, None

        return False, parse_result

    def parse_wheel_speed(self, data):
        '''
        Customer 1 parser

        in: CAN msg
        out: in [km/h]
            WHEEL_SPEED_FR
            WHEEL_SPEED_FL
            WHEEL_SPEED_RR
            WHEEL_SPEED_RL

        msg length: 8 bytes

        WHEEL_SPEED_RL: msb 8:22 bit
        WHEEL_SPEED_RR: msb 24:38 bit

        '''
        speed_rl = (data[1] + ((data[2] & 0x7F) << 8)) * 0.01
        speed_rl = 0 if speed_rl > 327.65 else speed_rl

        speed_rr = (data[3] + ((data[4] & 0x7F) << 8)) * 0.01
        speed_rr = 0 if speed_rr > 327.65 else speed_rr

        return (0, 0, speed_rr, speed_rl)


class Customer2Parser(AbstractParser):
    def __init__(self):
        super(Customer1Parser, self).__init__()

    def need_handle_speed_data(self, arbitration_id):
        return arbitration_id == 0xB6 #TODO

    def parse(self, message_type, data):
        parse_result = None
        if message_type == 'WHEEL_SPEED':
            parse_result = self.parse_wheel_speed(data)

        if not parse_result:
            return True, None

        return False, parse_result

    def parse_wheel_speed(self, data): #TODO
        '''
        Customer 1 parser

        in: CAN msg
        out: in [km/h]
            WHEEL_SPEED_FR
            WHEEL_SPEED_FL
            WHEEL_SPEED_RR
            WHEEL_SPEED_RL

        msg length: 8 bytes

        WHEEL_SPEED_RL: msb 8:22 bit
        WHEEL_SPEED_RR: msb 24:38 bit

        '''
        speed_rl = (data[1] + ((data[2] & 0x7F) << 8)) * 0.01
        speed_rl = 0 if speed_rl > 327.65 else speed_rl

        speed_rr = (data[3] + ((data[4] & 0x7F) << 8)) * 0.01
        speed_rr = 0 if speed_rr > 327.65 else speed_rr

        return (0, 0, speed_rr, speed_rl)


class CanParserFactory:
    def create(type: str = None) -> AbstractParser:
        try:
            if type == '' or type is None:
                instance = DefaultParser()
            else:
                instance = eval(type)()
        except Exception as ex:
            print(
                'Failed to initalize specified can parser:{0}, use default', format(type))
            instance = DefaultParser()

        return instance
