from .base import ProtocolBase

class SMBProtocol(ProtocolBase):
    def __init__(self):
        super().__init__("SMB")
    # Add SMB-specific methods if needed
