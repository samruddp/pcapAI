class ProtocolBase:
    def __init__(self, name):
        self.name = name

    def filter_packets(self, packets):
        """Default filtering: match by highest_layer or layer name."""
        filtered = []
        for pkt in packets:
            highest_layer = pkt.get("metadata", {}).get("highest_layer", "").upper()
            if highest_layer == self.name.upper():
                filtered.append(pkt)
                continue
            layers = pkt.get("layers", {})
            if self.name.lower() in layers:
                filtered.append(pkt)
        return filtered

    def analyze(self, packets):
        """Protocol-specific analysis (override in subclasses)."""
        return {
            "protocol": self.name,
            "packet_count": len(packets),
            "packets": packets  # Include the actual filtered packets
        }
