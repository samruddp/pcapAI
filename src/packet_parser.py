import pyshark
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class PacketParser:
    def __init__(self):
        self.supported_layers = {
            "eth": self._parse_ethernet_layer,
            "ip": self._parse_ip_layer,
            "ipv6": self._parse_ipv6_layer,
            "tcp": self._parse_tcp_layer,
            "udp": self._parse_udp_layer,
            "http": self._parse_http_layer,
            "dns": self._parse_dns_layer,
            "icmp": self._parse_icmp_layer,
            "arp": self._parse_arp_layer,
            "ssl": self._parse_ssl_layer,
            "tls": self._parse_tls_layer,
        }

    def parse_packet(self, packet) -> Dict[str, Any]:
        """
        Parse a pyshark packet object into a structured dictionary.

        Args:
            packet: pyshark packet object

        Returns:
            Dictionary containing parsed packet information
        """
        parsed_packet = {
            "metadata": self._extract_metadata(packet),
            "layers": {},
        }

        # Parse each layer in the packet
        for layer in packet.layers:
            layer_name = layer.layer_name.lower()

            if layer_name in self.supported_layers:
                parsed_packet["layers"][layer_name] = self.supported_layers[layer_name](
                    layer
                )
            else:
                parsed_packet["layers"][layer_name] = self._parse_generic_layer(layer)

        return parsed_packet

    def _extract_metadata(self, packet) -> Dict[str, Any]:
        """Extract basic packet metadata."""
        metadata = {}

        try:
            metadata["length"] = (
                int(packet.length) if hasattr(packet, "length") else None
            )
            metadata["captured_length"] = (
                int(packet.captured_length)
                if hasattr(packet, "captured_length")
                else None
            )
            metadata["sniff_time"] = (
                str(packet.sniff_time) if hasattr(packet, "sniff_time") else None
            )
            metadata["number"] = (
                int(packet.number) if hasattr(packet, "number") else None
            )
            metadata["highest_layer"] = (
                packet.highest_layer if hasattr(packet, "highest_layer") else None
            )
            metadata["interface_captured"] = (
                packet.interface_captured
                if hasattr(packet, "interface_captured")
                else None
            )
        except Exception as e:
            metadata["error"] = f"Error extracting metadata: {str(e)}"

        return metadata

    def _parse_ethernet_layer(self, layer) -> Dict[str, Any]:
        """Parse Ethernet layer."""
        eth_data = {}

        try:
            eth_data["src_mac"] = getattr(layer, "src", None)
            eth_data["dst_mac"] = getattr(layer, "dst", None)
            eth_data["type"] = getattr(layer, "type", None)

            # OUI information if available
            if hasattr(layer, "src_oui_resolved"):
                eth_data["src_vendor"] = getattr(layer, "src_oui_resolved", None)
            if hasattr(layer, "dst_oui_resolved"):
                eth_data["dst_vendor"] = getattr(layer, "dst_oui_resolved", None)

        except Exception as e:
            eth_data["error"] = str(e)

        return eth_data

    def _parse_ip_layer(self, layer) -> Dict[str, Any]:
        """Parse IP layer."""
        ip_data = {}

        try:
            ip_data["version"] = getattr(layer, "version", None)
            ip_data["src"] = getattr(layer, "src", None)
            ip_data["dst"] = getattr(layer, "dst", None)
            ip_data["protocol"] = getattr(layer, "proto", None)
            ip_data["ttl"] = getattr(layer, "ttl", None)
            ip_data["length"] = getattr(layer, "len", None)
            ip_data["id"] = getattr(layer, "id", None)
            ip_data["flags"] = getattr(layer, "flags", None)
            ip_data["fragment_offset"] = getattr(layer, "frag_offset", None)
            ip_data["header_length"] = getattr(layer, "hdr_len", None)
            ip_data["dsfield"] = getattr(layer, "dsfield", None)

        except Exception as e:
            ip_data["error"] = str(e)

        return ip_data

    def _parse_ipv6_layer(self, layer) -> Dict[str, Any]:
        """Parse IPv6 layer."""
        ipv6_data = {}

        try:
            ipv6_data["version"] = getattr(layer, "version", None)
            ipv6_data["src"] = getattr(layer, "src", None)
            ipv6_data["dst"] = getattr(layer, "dst", None)
            ipv6_data["next_header"] = getattr(layer, "nxt", None)
            ipv6_data["hop_limit"] = getattr(layer, "hlim", None)
            ipv6_data["payload_length"] = getattr(layer, "plen", None)
            ipv6_data["traffic_class"] = getattr(layer, "tclass", None)
            ipv6_data["flow_label"] = getattr(layer, "flow", None)

        except Exception as e:
            ipv6_data["error"] = str(e)

        return ipv6_data

    def _parse_tcp_layer(self, layer) -> Dict[str, Any]:
        """Parse TCP layer."""
        tcp_data = {}

        try:
            tcp_data["src_port"] = getattr(layer, "srcport", None)
            tcp_data["dst_port"] = getattr(layer, "dstport", None)
            tcp_data["seq"] = getattr(layer, "seq", None)
            tcp_data["ack"] = getattr(layer, "ack", None)
            tcp_data["window_size"] = getattr(layer, "window_size_value", None)
            tcp_data["flags"] = getattr(layer, "flags", None)
            tcp_data["header_length"] = getattr(layer, "hdr_len", None)
            tcp_data["checksum"] = getattr(layer, "checksum", None)
            tcp_data["urgent_pointer"] = getattr(layer, "urgent_pointer", None)
            tcp_data["stream"] = getattr(layer, "stream", None)

            # Parse TCP flags if available
            if hasattr(layer, "flags"):
                flags_obj = getattr(layer, "flags")
                tcp_data["flags_detailed"] = {
                    "syn": getattr(flags_obj, "syn", None),
                    "ack": getattr(flags_obj, "ack", None),
                    "fin": getattr(flags_obj, "fin", None),
                    "rst": getattr(flags_obj, "reset", None),
                    "psh": getattr(flags_obj, "push", None),
                    "urg": getattr(flags_obj, "urg", None),
                }

        except Exception as e:
            tcp_data["error"] = str(e)

        return tcp_data

    def _parse_udp_layer(self, layer) -> Dict[str, Any]:
        """Parse UDP layer."""
        udp_data = {}

        try:
            udp_data["src_port"] = getattr(layer, "srcport", None)
            udp_data["dst_port"] = getattr(layer, "dstport", None)
            udp_data["length"] = getattr(layer, "length", None)
            udp_data["checksum"] = getattr(layer, "checksum", None)
            udp_data["stream"] = getattr(layer, "stream", None)

        except Exception as e:
            udp_data["error"] = str(e)

        return udp_data

    def _parse_http_layer(self, layer) -> Dict[str, Any]:
        """Parse HTTP layer."""
        http_data = {}

        try:
            # Request fields
            http_data["method"] = getattr(layer, "request_method", None)
            http_data["uri"] = getattr(layer, "request_uri", None)
            http_data["version"] = getattr(layer, "request_version", None)
            http_data["host"] = getattr(layer, "host", None)
            http_data["user_agent"] = getattr(layer, "user_agent", None)

            # Response fields
            http_data["response_code"] = getattr(layer, "response_code", None)
            http_data["response_phrase"] = getattr(layer, "response_phrase", None)
            http_data["content_type"] = getattr(layer, "content_type", None)
            http_data["content_length"] = getattr(layer, "content_length", None)

        except Exception as e:
            http_data["error"] = str(e)

        return http_data

    def _parse_dns_layer(self, layer) -> Dict[str, Any]:
        """Parse DNS layer."""
        dns_data = {}

        try:
            dns_data["id"] = getattr(layer, "id", None)
            dns_data["flags"] = getattr(layer, "flags", None)
            dns_data["qr"] = getattr(layer, "qr", None)
            dns_data["opcode"] = getattr(layer, "opcode", None)
            dns_data["rcode"] = getattr(layer, "rcode", None)
            dns_data["qd_count"] = getattr(layer, "count_queries", None)
            dns_data["an_count"] = getattr(layer, "count_answers", None)
            dns_data["ns_count"] = getattr(layer, "count_auth_rr", None)
            dns_data["ar_count"] = getattr(layer, "count_add_rr", None)

            # Query information
            dns_data["query_name"] = getattr(layer, "qry_name", None)
            dns_data["query_type"] = getattr(layer, "qry_type", None)
            dns_data["query_class"] = getattr(layer, "qry_class", None)

        except Exception as e:
            dns_data["error"] = str(e)

        return dns_data

    def _parse_icmp_layer(self, layer) -> Dict[str, Any]:
        """Parse ICMP layer."""
        icmp_data = {}

        try:
            icmp_data["type"] = getattr(layer, "type", None)
            icmp_data["code"] = getattr(layer, "code", None)
            icmp_data["checksum"] = getattr(layer, "checksum", None)
            icmp_data["id"] = getattr(layer, "id", None)
            icmp_data["seq"] = getattr(layer, "seq", None)

        except Exception as e:
            icmp_data["error"] = str(e)

        return icmp_data

    def _parse_arp_layer(self, layer) -> Dict[str, Any]:
        """Parse ARP layer."""
        arp_data = {}

        try:
            arp_data["hardware_type"] = getattr(layer, "hw_type", None)
            arp_data["protocol_type"] = getattr(layer, "proto_type", None)
            arp_data["opcode"] = getattr(layer, "opcode", None)
            arp_data["src_hw"] = getattr(layer, "src_hw_mac", None)
            arp_data["src_proto"] = getattr(layer, "src_proto_ipv4", None)
            arp_data["dst_hw"] = getattr(layer, "dst_hw_mac", None)
            arp_data["dst_proto"] = getattr(layer, "dst_proto_ipv4", None)

        except Exception as e:
            arp_data["error"] = str(e)

        return arp_data

    def _parse_ssl_layer(self, layer) -> Dict[str, Any]:
        """Parse SSL/TLS layer."""
        ssl_data = {}

        try:
            ssl_data["version"] = getattr(layer, "version", None)
            ssl_data["content_type"] = getattr(layer, "content_type", None)
            ssl_data["length"] = getattr(layer, "length", None)
            ssl_data["handshake_type"] = getattr(layer, "handshake_type", None)

        except Exception as e:
            ssl_data["error"] = str(e)

        return ssl_data

    def _parse_tls_layer(self, layer) -> Dict[str, Any]:
        """Parse TLS layer."""
        return self._parse_ssl_layer(layer)  # TLS and SSL parsing is similar

    def _parse_generic_layer(self, layer) -> Dict[str, Any]:
        """Parse any layer generically."""
        generic_data = {}

        try:
            # Get all field names for this layer
            if hasattr(layer, "field_names"):
                for field_name in layer.field_names:
                    try:
                        field_value = getattr(layer, field_name)
                        generic_data[field_name] = str(field_value)
                    except Exception:
                        continue

            # If no field_names, try to get common attributes
            if not generic_data:
                for attr_name in dir(layer):
                    if not attr_name.startswith("_") and not callable(
                        getattr(layer, attr_name)
                    ):
                        try:
                            attr_value = getattr(layer, attr_name)
                            generic_data[attr_name] = str(attr_value)
                        except Exception:
                            continue

        except Exception as e:
            generic_data["error"] = str(e)

        return generic_data

    def parse_packets_to_json(self, packets: List) -> str:
        """
        Parse a list of packets and return JSON string.

        Args:
            packets: List of pyshark packet objects

        Returns:
            JSON string containing parsed packets
        """
        parsed_packets = []

        for i, packet in enumerate(packets):
            try:
                parsed_packet = self.parse_packet(packet)
                parsed_packet["packet_index"] = i
                parsed_packets.append(parsed_packet)
            except Exception as e:
                parsed_packets.append(
                    {"packet_index": i, "error": f"Failed to parse packet: {str(e)}"}
                )

        return json.dumps(parsed_packets, default=str)
