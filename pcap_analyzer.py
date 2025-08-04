import pyshark
from collections import defaultdict, Counter
import json

class PcapAnalyzer:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        self.packets = []
        self.analysis = {}
    
    def analyze(self):
        """Analyze the pcap file and extract relevant information."""
        print("Loading and analyzing pcap file...")
        
        try:
            cap = pyshark.FileCapture(self.pcap_file)
            
            protocols = Counter()
            src_ips = Counter()
            dst_ips = Counter()
            src_ports = Counter()
            dst_ports = Counter()
            packet_sizes = []
            
            packet_count = 0
            for packet in cap:
                packet_count += 1
                
                # Extract protocols
                for layer in packet.layers:
                    protocols[layer.layer_name] += 1
                
                # Extract IP information if available
                if hasattr(packet, 'ip'):
                    src_ips[packet.ip.src] += 1
                    dst_ips[packet.ip.dst] += 1
                    packet_sizes.append(int(packet.length))
                
                # Extract port information if available
                if hasattr(packet, 'tcp'):
                    src_ports[packet.tcp.srcport] += 1
                    dst_ports[packet.tcp.dstport] += 1
                elif hasattr(packet, 'udp'):
                    src_ports[packet.udp.srcport] += 1
                    dst_ports[packet.udp.dstport] += 1
            
            cap.close()
            
            # Compile analysis results
            self.analysis = {
                'total_packets': packet_count,
                'protocols': dict(protocols.most_common(10)),
                'top_source_ips': dict(src_ips.most_common(10)),
                'top_destination_ips': dict(dst_ips.most_common(10)),
                'top_source_ports': dict(src_ports.most_common(10)),
                'top_destination_ports': dict(dst_ports.most_common(10)),
                'avg_packet_size': sum(packet_sizes) / len(packet_sizes) if packet_sizes else 0,
                'min_packet_size': min(packet_sizes) if packet_sizes else 0,
                'max_packet_size': max(packet_sizes) if packet_sizes else 0
            }
            
            print(f"Analysis complete. Processed {packet_count} packets.")
            return self.analysis
            
        except Exception as e:
            raise Exception(f"Error analyzing pcap file: {e}")
    
    def get_summary(self):
        """Get a human-readable summary of the analysis."""
        if not self.analysis:
            return "No analysis data available."
        
        summary = f"""
Packet Trace Analysis Summary:
- Total packets: {self.analysis['total_packets']}
- Top protocols: {', '.join(self.analysis['protocols'].keys())}
- Average packet size: {self.analysis['avg_packet_size']:.2f} bytes
- Top source IPs: {', '.join(list(self.analysis['top_source_ips'].keys())[:3])}
- Top destination IPs: {', '.join(list(self.analysis['top_destination_ips'].keys())[:3])}
"""
        return summary.strip()
