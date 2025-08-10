"""
Unified filtering tool with multiple filter methods.
"""
import json


class Filter:
    """Unified filter tool with multiple filtering methods."""
    
    def get_tool_definitions(self):
        """Return all OpenAI function definitions for filtering tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "filter_packets_by_protocol",
                    "description": "Filter packets by protocol type (e.g., nfs, smb2, http) and return them as a JSON object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "protocol": {
                                "type": "string",
                                "description": "Protocol to filter by (e.g., 'nfs', 'smb2', 'http', 'tcp', 'udp')"
                            }
                        },
                        "required": ["protocol"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_packets_by_ip",
                    "description": "Filter packets from a specific source IP address for any protocol and return them as a JSON object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_ip": {
                                "type": "string",
                                "description": "Source IP address to filter packets by (e.g., '192.168.1.100')"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "Optional: Protocol to filter by (e.g., 'nfs', 'smb2', 'http'). If not specified, filters all protocols."
                            }
                        },
                        "required": ["source_ip"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_packets_by_operation",
                    "description": "Filter packets by protocol operation/procedure (e.g., write, read, create, lookup) and return them as a JSON object",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation/procedure to filter by (e.g., 'write', 'read', 'create', 'lookup', 'open', 'close')"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "Optional: Protocol to filter by (e.g., 'nfs', 'smb2', 'http'). If not specified, searches all protocols."
                            }
                        },
                        "required": ["operation"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name, arguments, analysis_data):
        """Execute the specified filter method."""
        if tool_name == "filter_packets_by_protocol":
            return self.filter_by_protocol(arguments, analysis_data)
        elif tool_name == "filter_packets_by_ip":
            return self.filter_by_ip(arguments, analysis_data)
        elif tool_name == "filter_packets_by_operation":
            return self.filter_by_operation(arguments, analysis_data)
        else:
            return {
                "status": "error",
                "message": f"Unknown filter tool: {tool_name}",
                "packets_filtered": 0
            }
    
    def filter_by_protocol(self, arguments, analysis_data):
        """Filter packets by protocol type."""
        packets = analysis_data.get("packets", [])
        protocol_filter = arguments.get("protocol", "").lower()
        
        if not protocol_filter:
            return {
                "status": "error",
                "message": "Protocol is required for this filter",
                "packets_filtered": 0
            }
        
        filtered_packets = []
        
        for packet in packets:
            if isinstance(packet, dict):
                # Check for protocol in layers
                layers = packet.get("layers", {})
                metadata = packet.get("metadata", {})
                
                # Check if this packet matches the protocol
                is_match = False
                
                # Check in layers
                if protocol_filter in [layer.lower() for layer in layers.keys()]:
                    is_match = True
                # Check in metadata highest layer
                elif metadata.get("highest_layer", "").lower() == protocol_filter:
                    is_match = True
                # Check for protocol variations (e.g., smb2 might be stored as smb)
                elif protocol_filter == "smb2" and "smb" in [layer.lower() for layer in layers.keys()]:
                    is_match = True
                # Check for common protocol aliases
                elif protocol_filter == "http" and any(layer.lower() in ["http", "https"] for layer in layers.keys()):
                    is_match = True
                
                if is_match:
                    filtered_packets.append(packet)
        
        # Return filtered data as JSON object
        filtered_data = {
            "total_packets": len(filtered_packets),
            "filter_type": f"{protocol_filter.upper()} Protocol",
            "protocol_filter": protocol_filter,
            "packets": filtered_packets
        }
        
        return {
            "status": "success",
            "message": f"Filtered {len(filtered_packets)} {protocol_filter.upper()} packets",
            "packets_filtered": len(filtered_packets),
            "protocol_filter": protocol_filter,
            "filtered_data": filtered_data
        }
    
    def filter_by_ip(self, arguments, analysis_data):
        """Filter packets by source IP address, optionally for a specific protocol."""
        packets = analysis_data.get("packets", [])
        source_ip_filter = arguments.get("source_ip")
        protocol_filter = arguments.get("protocol", "").lower()
        
        if not source_ip_filter:
            return {
                "status": "error",
                "message": "Source IP address is required for this filter",
                "packets_filtered": 0
            }
        
        filtered_packets = []
        
        for packet in packets:
            if isinstance(packet, dict):
                # Check protocol if specified
                protocol_match = True
                if protocol_filter:
                    layers = packet.get("layers", {})
                    metadata = packet.get("metadata", {})
                    
                    protocol_match = False
                    # Check in layers
                    if protocol_filter in [layer.lower() for layer in layers.keys()]:
                        protocol_match = True
                    # Check in metadata highest layer
                    elif metadata.get("highest_layer", "").lower() == protocol_filter:
                        protocol_match = True
                    # Check for protocol variations
                    elif protocol_filter == "smb2" and "smb" in [layer.lower() for layer in layers.keys()]:
                        protocol_match = True
                    elif protocol_filter == "http" and any(layer.lower() in ["http", "https"] for layer in layers.keys()):
                        protocol_match = True
                
                if protocol_match:
                    # Check source IP address
                    packet_source_ip = None
                    layers = packet.get("layers", {})
                    metadata = packet.get("metadata", {})
                    
                    # Try to get source IP from different possible locations
                    if "ip" in layers:
                        ip_layer = layers.get("ip", {})
                        packet_source_ip = ip_layer.get("src") or ip_layer.get("src_host")
                    
                    # Also check metadata
                    if not packet_source_ip:
                        packet_source_ip = metadata.get("src_ip") or metadata.get("source_ip")
                    
                    # Also check top-level packet fields
                    if not packet_source_ip:
                        packet_source_ip = packet.get("src_ip") or packet.get("source_ip")
                    
                    # Add packet if source IP matches filter
                    if packet_source_ip == source_ip_filter:
                        filtered_packets.append(packet)
        
        # Return filtered data as JSON object
        protocol_text = f" {protocol_filter.upper()}" if protocol_filter else ""
        filter_type = f"{protocol_text} Packets from Source IP: {source_ip_filter}".strip()
        
        filtered_data = {
            "total_packets": len(filtered_packets),
            "filter_type": filter_type,
            "source_ip_filter": source_ip_filter,
            "protocol_filter": protocol_filter if protocol_filter else None,
            "packets": filtered_packets
        }
        
        return {
            "status": "success",
            "message": f"Filtered {len(filtered_packets)}{protocol_text.lower()} packets from source IP {source_ip_filter}",
            "packets_filtered": len(filtered_packets),
            "source_ip_filter": source_ip_filter,
            "protocol_filter": protocol_filter,
            "filtered_data": filtered_data
        }
    
    def filter_by_operation(self, arguments, analysis_data):
        """Filter packets by operation/procedure type."""
        packets = analysis_data.get("packets", [])
        operation_filter = arguments.get("operation", "").lower()
        protocol_filter = arguments.get("protocol", "").lower()
        
        if not operation_filter:
            return {
                "status": "error",
                "message": "Operation is required for this filter",
                "packets_filtered": 0
            }
        
        filtered_packets = []
        
        for packet in packets:
            if isinstance(packet, dict):
                layers = packet.get("layers", {})
                metadata = packet.get("metadata", {})
                
                # First check protocol if specified
                protocol_match = True
                if protocol_filter:
                    protocol_match = False
                    # Check in layers
                    if protocol_filter in [layer.lower() for layer in layers.keys()]:
                        protocol_match = True
                    # Check in metadata highest layer
                    elif metadata.get("highest_layer", "").lower() == protocol_filter:
                        protocol_match = True
                    # Check for protocol variations
                    elif protocol_filter == "smb2" and "smb" in [layer.lower() for layer in layers.keys()]:
                        protocol_match = True
                    elif protocol_filter == "http" and any(layer.lower() in ["http", "https"] for layer in layers.keys()):
                        protocol_match = True
                
                if protocol_match:
                    # Check for operation in packet data
                    operation_match = False
                    
                    # Check in all layers for operation/procedure information
                    for layer_name, layer_data in layers.items():
                        if isinstance(layer_data, dict):
                            # Check for common operation field names
                            for field in ["procedure", "operation", "opcode", "command", "method", "request_type"]:
                                if field in layer_data:
                                    field_value = str(layer_data[field]).lower()
                                    if operation_filter in field_value:
                                        operation_match = True
                                        break
                            
                            # Also check in nested fields
                            for key, value in layer_data.items():
                                if isinstance(value, (str, int)):
                                    if operation_filter in str(value).lower():
                                        operation_match = True
                                        break
                            
                            if operation_match:
                                break
                    
                    # Check in metadata for operation info
                    if not operation_match:
                        for key, value in metadata.items():
                            if isinstance(value, (str, int)):
                                if operation_filter in str(value).lower():
                                    operation_match = True
                                    break
                    
                    # Check in top-level packet fields
                    if not operation_match:
                        for key, value in packet.items():
                            if key not in ["layers", "metadata"] and isinstance(value, (str, int)):
                                if operation_filter in str(value).lower():
                                    operation_match = True
                                    break
                    
                    if operation_match:
                        filtered_packets.append(packet)
        
        # Return filtered data as JSON object
        protocol_text = f" {protocol_filter.upper()}" if protocol_filter else ""
        filter_type = f"{protocol_text} {operation_filter.upper()} Operations".strip()
        
        filtered_data = {
            "total_packets": len(filtered_packets),
            "filter_type": filter_type,
            "operation_filter": operation_filter,
            "protocol_filter": protocol_filter if protocol_filter else None,
            "packets": filtered_packets
        }
        
        return {
            "status": "success",
            "message": f"Filtered {len(filtered_packets)}{protocol_text.lower()} {operation_filter.upper()} operation packets",
            "packets_filtered": len(filtered_packets),
            "operation_filter": operation_filter,
            "protocol_filter": protocol_filter,
            "filtered_data": filtered_data
        }
