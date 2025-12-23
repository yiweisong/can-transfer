import can
from ..common.context import AppContext
from ..typings import CanOptions

class CanTransfer:
    def __init__(self, options: CanOptions):
        if AppContext.can_bus is None:
            AppContext.can_bus = can.interface.Bus(
                channel=options.channel, 
                bustype='canalystii', 
                bitrate=options.bitrate
            )
        
        self.can = AppContext.can_bus
    
    def send(self, data):
        self.can.send(data)
