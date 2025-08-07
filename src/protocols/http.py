from .base import ProtocolBase

class HTTPProtocol(ProtocolBase):
    def __init__(self):
        super().__init__("HTTP")
    # Add HTTP-specific methods if needed
