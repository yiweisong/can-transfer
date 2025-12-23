import can

class Context:
    config: dict = {}
    can_bus: can.interface.Bus = None
    
AppContext = Context()