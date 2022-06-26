from abc import ABCMeta, abstractmethod
import struct
from typing import List
from pyee import EventEmitter
import math

from ..typings import (OdometerOptions, ComputorOptions, ConvertorOptions,
                       SignalOptions, SignalParameter, MapConvertorParameter,
                       MessageValue)


def build_computor(options: ComputorOptions):
    if options and options.method == 'avg':
        return AvgComputor(options)

    if options and options.method == 'raw':
        return RawComputor(options)

    return None


def build_convertor(options: ConvertorOptions):
    if options and options.method == 'map':
        return MapConvertor(options)

    return None


def build_signal_parser(name, options: SignalOptions):
    if options is None:
        return None
    return SignalParser(name, options)


def calculate(parameter: SignalParameter, data: bytes) -> MessageValue:
    start_byte_pos = math.floor(parameter.start/8)
    end_byte_pos = math.ceil((parameter.start+parameter.length)/8)

    value_bytes = data[start_byte_pos:end_byte_pos]
    len_of_value = len(value_bytes)

    if len_of_value == 1:
        value = value_bytes[0] & (int(math.pow(2, parameter.length))-1)

    elif len_of_value == 2:
        abs = (int(math.pow(2, parameter.length))-1)
        fmt = '<H' if parameter.protocol == 'intel' else '>H'
        value = struct.unpack(fmt, value_bytes)[0] & abs

    else:
        raise Exception('Cannot calculate')

    value = value * parameter.scale + parameter.offset

    if parameter.range:
        return min(max(value, parameter.range[0]), parameter.range[1])

    return value


class AvgComputor:
    _parameters: List[SignalParameter] = []

    def __init__(self, options: ComputorOptions):
        for parameter in options.params:
            self._parameters.append(
                SignalParameter(parameter)
            )

    def use(self, data: bytes) -> MessageValue:
        total = 0
        param_len = len(self._parameters)

        for parameter in self._parameters:
            value = calculate(parameter, data)
            total += value

        return total/param_len


class RawComputor:
    _parameter: SignalParameter

    def __init__(self, options: ComputorOptions):
        self._parameter = SignalParameter(options.params)

    def use(self, data: bytes) -> MessageValue:
        return calculate(self._parameter, data)


class MapConvertor:
    _parameters: List[MapConvertorParameter]=[]

    def __init__(self, options: ConvertorOptions):
        for parameter in options.params:
            self._parameters.append(
                MapConvertorParameter(
                    parameter.get('key'),
                    parameter.get('value')
                )
            )

    def use(self, data: MessageValue) -> MessageValue:
        return next((item.value for item in self._parameters
                     if item.key == data), 1)


class SignalParser:
    _computor = None
    _convertor = None
    _name = None

    def __init__(self, name: str, options: SignalOptions):
        self._name = name

        self._computor = build_computor(options.compute)
        self._convertor = build_convertor(options.convert)

    def parse(self, data) -> MessageValue:
        last_value = None

        if self._computor:
            last_value = self._computor.use(data)

        if self._convertor and last_value is not None:
            last_value = self._convertor.use(last_value)

        if last_value is None:
            raise Exception(
                'Cannot finish signal parse of [{0}]'.format(self._name))

        return last_value


class OdometerParser(EventEmitter):
    _wheel_speed: float = 0
    _gear: int = 1
    _speed_id: int = None
    _gear_id: int = None
    _speed_signal_parser: SignalParser = None
    _gear_signal_parser: SignalParser = None

    def __init__(self, options: OdometerOptions):
        super(OdometerParser, self).__init__()
        self._wheel_speed = 0
        self._gear = 1

        self._speed_id = options.speed_id
        self._gear_id = options.gear_id
        self._speed_signal_parser = build_signal_parser(
            'Speed', options.speed)
        self._gear_signal_parser = build_signal_parser(
            'Gear', options.gear)

    def parse(self, data):
        if self._speed_signal_parser and data.arbitration_id == self._speed_id:
            self._wheel_speed = self._speed_signal_parser.parse(data.data)
            self.emit('data', data.timestamp, self._wheel_speed * self._gear)
            return

        if self._gear_signal_parser and data.arbitration_id == self._gear_id:
            self._gear = self._gear_signal_parser.parse(data.data)
            return
