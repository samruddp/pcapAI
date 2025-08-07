from .base import ProtocolBase

class NFSProtocol(ProtocolBase):
    def __init__(self):
        super().__init__("NFS")
    # Add NFS-specific methods if needed
