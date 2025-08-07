import pyshark
from src.packet_parser import PacketParser

class ProtocolBase:
    def __init__(self, name):
        self.name = name

    def filter_packets(self, pcap_file):
        """Use PyShark display filter for protocol and return JSON-serializable dicts."""
        parser = PacketParser()
        display_filter = self.name.lower()
        cap = pyshark.FileCapture(pcap_file, display_filter=display_filter)
        packets = []
        for pkt in cap:
            pkt_info = parser.parse_packet(pkt)  # Should return a dict
            packets.append(pkt_info)
        cap.close()
        return packets

    def analyze(self, packets):
        return {
            "protocol": self.name,
            "packet_count": len(packets),
            "packets": packets,
        }
