class UartOptions:
    _path: str
    _baudrate: int

    def __init__(self, path: str, baudrate: int) -> None:
        self._path = path
        self._baudrate = baudrate

    @property
    def path(self):
        return self._path

    @property
    def baudrate(self):
        return self._baudrate


class CanOptions:
    _channel: str
    _bitrate: int

    def __init__(self, channel: str, bitrate: int) -> None:
        self._channel = channel
        self._bitrate = bitrate

    @property
    def channel(self):
        return self._channel

    @property
    def bitrate(self):
        return self._bitrate


class UartMessageBody:
    _type: str
    _data: any

    def __init__(self, type: str, data: any) -> None:
        self._type = type
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def data(self):
        return self._data
    