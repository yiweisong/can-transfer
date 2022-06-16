from abc import ABCMeta, abstractmethod

from pyee import EventEmitter


class AbstractParser(EventEmitter):
    __metaclass__ = ABCMeta
    _type = ''

    @abstractmethod
    def parse(self, data):
        '''
        parse message
        '''

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value


class DefaultParser(AbstractParser):
    _wheel_speed: float = 0
    _gear: int = 1

    def __init__(self):
        super(DefaultParser, self).__init__()
        self._wheel_speed = 0
        self._gear = 1

    def parse(self, data):
        if data.arbitration_id == 0xAA:
            self._wheel_speed = self.parse_wheel_speed(data.data)
            self.emit('data', self._wheel_speed * self._gear)

        if data.arbitration_id == 0x3BC:
            self._gear = self.parse_gear(data.data)

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
        speed_rr = (data[4] * 256 + data[5]) * scale + offset
        speed_rl = (data[6] * 256 + data[7]) * scale + offset
        return (speed_rr + speed_rl)/2

    def parse_gear(self, data):
        gear = data[1] & 0x3F

        if gear == 32:
            return 0

        if gear == 16:
            return -1

        if gear == 8:
            return 0

        if gear == 0:
            return 1

        return 0


class Customer1Parser(AbstractParser):
    '''
        Customer: FAW
    '''
    _wheel_speed: float = 0
    _gear: int = 1

    def __init__(self):
        super(Customer1Parser, self).__init__()
        self._wheel_speed = 0
        self._gear = 1

    def parse(self, data):
        if data.arbitration_id == 0xB6:
            self._wheel_speed = self.parse_wheel_speed(data.data)
            self.emit('data', self._wheel_speed * self._gear)

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

        return (speed_rr + speed_rl)/2


class Customer2Parser(AbstractParser):
    '''
        Customer: Inceptio
    '''
    _wheel_speed: float = 0
    _gear: int = 1

    def __init__(self):
        super(Customer2Parser, self).__init__()
        self._wheel_speed = 0
        self._gear = 1

    def parse(self, data):
        if data.arbitration_id == 0x08fe6e0b:
            self._wheel_speed = self.parse_wheel_speed(data.data)
            self.emit('data', self._wheel_speed * self._gear)

    def parse_wheel_speed(self, data):
        '''
        Customer 2 parser

        in: CAN msg
        out: in [km/h]
            WHEEL_SPEED_FR
            WHEEL_SPEED_FL
            WHEEL_SPEED_RR
            WHEEL_SPEED_RL

        msg length: 8 bytes

        SteerAxleLeftWheelSpeed: little endian 0:16 bit
        SteerAxleRightWheelSpeed: little endian 16:32 bit
        DrivenAxleLeftWheelSpeed: little endian 32:48 bit
        DrivenAxleRightWheelSpeed: little endian 48:64 bit

        '''
        scale = 0.00390625
        max_value = 250.996
        speed_fr = (data[0] + data[1] * 256) * scale
        speed_fl = (data[2] + data[3] * 256) * scale
        speed_rr = (data[4] + data[5] * 256) * scale
        speed_rl = (data[6] + data[7] * 256) * scale

        return (min(speed_rr, max_value) + min(speed_rl, max_value))/2


class VoyahParser(AbstractParser):
    _wheel_speed: float = 0
    _gear: int = 1

    def __init__(self):
        super(VoyahParser, self).__init__()
        self._wheel_speed = 0
        self._gear = 1

    def parse(self, data):
        if data.arbitration_id == 0x122:
            self._wheel_speed = self.parse_wheel_speed(data.data)
            self.emit('data', self._wheel_speed * self._gear)

    def parse_wheel_speed(self, data):
        '''
        Parse WHEEL_SPEEDS info from Voyah.

        in: CAN msg
        out: in [km/h]
            WHEEL_SPEED_RL
            WHEEL_SPEED_RR

        dbc: MSB, unsigned
        '''
        offset = 0
        scale = 0.05625
        max_value = 270
        speed_rr = (data[0]+((data[1] & 0x1F) << 8)) * scale + offset
        speed_rl = (data[2]+((data[3] & 0x1F) << 8)) * scale + offset
        return (min(speed_rr, max_value) + min(speed_rl, max_value))/2


class TrunkParer(AbstractParser):
    _wheel_speed: float = 0
    _gear: int = 1

    def __init__(self):
        super(TrunkParer, self).__init__()
        self._wheel_speed = 0
        self._gear = 1

    def parse(self, data):
        if data.arbitration_id == 0x8FE6EFE:
            self._wheel_speed = self.parse_wheel_speed(data.data)
            self.emit('data', self._wheel_speed * self._gear)

    def parse_wheel_speed(self, data):
        '''
        Trunk parser

        in: CAN msg
        out: in [km/h]
            WHEEL_SPEED_FR
            WHEEL_SPEED_FL
            WHEEL_SPEED_RR
            WHEEL_SPEED_RL

        msg length: 8 bytes

        FrontAxleLeftWheelSpeed: little endian 0:16 bit
        FrontAxleRightWheelSpeed: little endian 16:32 bit
        RearAxleLeftWheelSpeed: little endian 32:48 bit
        RearAxleRightWheelSpeed: little endian 48:64 bit

        '''
        scale = 0.00390625
        max_value = 250.996
        speed_fr = (data[0] + data[1] * 256) * scale
        speed_fl = (data[2] + data[3] * 256) * scale
        speed_rr = (data[4] + data[5] * 256) * scale
        speed_rl = (data[6] + data[7] * 256) * scale

        return (min(speed_rr, max_value) + min(speed_rl, max_value))/2

class CanParserFactory:
    def create(type: str = None) -> AbstractParser:
        try:
            if type == '' or type is None:
                instance = DefaultParser()
            else:
                instance = eval(type)()
        except Exception as ex:
            print(
                'Failed to initalize specified can parser:{0}, use default'.format(type))
            instance = DefaultParser()

        instance.type = type
        return instance
