"""
Unified filtering tool with multiple filter methods.
"""
import json
import pyshark
from src.packet_parser import PacketParser


class Filter:
    """Unified filter tool with multiple filtering methods."""
    
    def __init__(self, session=None):
        """Initialize filter with optional session reference for pcap file access."""
        self.session = session
        self.packet_parser = PacketParser()
    
    def apply_pyshark_filter(self, filter_string, max_packets=1000):
        """Apply pyshark filter directly to the pcap file."""
        if not self.session or not self.session.pcap_file:
            print("[DEBUG] No pcap file available in session")
            return {
                "status": "error",
                "message": "No pcap file available",
                "packets_filtered": 0
            }
            
        if not filter_string:
            print("[DEBUG] No filter string provided")
            return {
                "status": "error", 
                "message": "No filter string provided",
                "packets_filtered": 0
            }
            
        pcap_file = self.session.pcap_file
        print(f"[DEBUG] Applying pyshark filter '{filter_string}' to {pcap_file}")
        
        try:
            # Use pyshark FileCapture with display filter
            capture = pyshark.FileCapture(pcap_file, display_filter=filter_string)
            
            # Convert packets to list
            filtered_packets = list(capture)
            capture.close()
            
            print(f"[DEBUG] Filtered capture complete: {len(filtered_packets)} packets found")
            
            if not filtered_packets:
                print("[DEBUG] No packets matched the filter")
                return {
                    "status": "success",
                    "message": f"No packets matched filter '{filter_string}'",
                    "packets_filtered": 0,
                    "filter_applied": filter_string,
                    "filtered_data": {"packets": [], "total_packets": 0}
                }
            
            # Convert to JSON using packet parser
            print("[DEBUG] Converting filtered packets to JSON...")
            json_data = self.packet_parser.parse_packets_to_json(filtered_packets)
            
            # Parse the JSON to get packet list
            parsed_packets = json.loads(json_data)
            
            print(f"[DEBUG] Successfully converted {len(parsed_packets)} packets to JSON")
            
            filtered_data = {
                "total_packets": len(parsed_packets),
                "filter_type": f"PyShark Filter: {filter_string}",
                "filter_applied": filter_string,
                "packets": parsed_packets
            }
            
            return {
                "status": "success",
                "message": f"Applied pyshark filter '{filter_string}' and found {len(parsed_packets)} matching packets",
                "packets_filtered": len(parsed_packets),
                "filter_applied": filter_string,
                "filtered_data": filtered_data
            }
            
        except Exception as e:
            error_msg = f"Error applying pyshark filter: {str(e)}"
            print(f"[DEBUG] {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "filter_applied": filter_string,
                "packets_filtered": 0
            }
    
    def get_tool_definitions(self):
        """Return all OpenAI function definitions for filtering tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "filter_packets_by_protocol",
                    "description": "Filter packets by protocol type (e.g., nfs, smb2, http) using pyshark filter or protocol name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "protocol": {
                                "type": "string",
                                "description": "Protocol to filter by (e.g., 'nfs', 'smb2', 'http', 'tcp', 'udp')"
                            },
                            "pyshark_filter": {
                                "type": "string",
                                "description": "Optional: Direct pyshark filter string (e.g., 'nfs', 'smb2', 'tcp.port == 80'). If provided, this takes precedence over protocol parameter."
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
                    "description": "Filter packets from a specific source IP address using pyshark filter or IP address",
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
                            },
                            "pyshark_filter": {
                                "type": "string",
                                "description": "Optional: Direct pyshark filter string (e.g., 'ip.src == 192.168.1.100', 'ip.addr == 192.168.1.100 and nfs'). If provided, this takes precedence over other parameters."
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
                    "description": "Filter packets by protocol operation/procedure using pyshark filter",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation/procedure to filter by (e.g., 'write', 'read', 'create', 'lookup', 'open', 'close')"
                            },
                            "pyshark_filter": {
                                "type": "string",
                                "description": "PyShark filter to be applied on pcap file based on operation. For example 'smb2.cmd == 5' for smb2 create request, 'nfs.procedure_v3 == 7' for NFS write"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "Optional: Protocol to filter by (e.g., 'nfs', 'smb2', 'http'). If not specified, searches all protocols."
                            }
                        },
                        "required": ["pyshark_filter"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name, arguments, analysis_data):
        """Execute the specified filter method."""
        print(f"[DEBUG] Executing filter tool: {tool_name}")
        print(f"[DEBUG] Tool arguments: {arguments}")
        print(f"[DEBUG] Analysis data keys: {list(analysis_data.keys())}")
        print(f"[DEBUG] Total packets in analysis_data: {len(analysis_data.get('packets', []))}")
        
        if tool_name == "filter_packets_by_protocol":
            return self.filter_by_protocol(arguments, analysis_data)
        elif tool_name == "filter_packets_by_ip":
            return self.filter_by_ip(arguments, analysis_data)
        elif tool_name == "filter_packets_by_operation":
            return self.filter_by_operation(arguments, analysis_data)
        else:
            print(f"[DEBUG] ERROR: Unknown filter tool: {tool_name}")
            return {
                "status": "error",
                "message": f"Unknown filter tool: {tool_name}",
                "packets_filtered": 0
            }
    
    def filter_by_protocol(self, arguments, analysis_data):
        """Filter packets by protocol type."""
        protocol_filter = arguments.get("protocol", "").lower()
        pyshark_filter = arguments.get("pyshark_filter", "").strip()
        
        print(f"[DEBUG] Protocol Filter - Input: protocol={protocol_filter}, pyshark_filter={pyshark_filter}")
        
        # If pyshark filter is provided, use it directly
        if pyshark_filter:
            print(f"[DEBUG] Using pyshark filter: {pyshark_filter}")
            return self.apply_pyshark_filter(pyshark_filter)
        
        # Fallback to protocol name as pyshark filter
        if protocol_filter:
            print(f"[DEBUG] Using protocol as pyshark filter: {protocol_filter}")
            return self.apply_pyshark_filter(protocol_filter)
        
        print("[DEBUG] Protocol Filter - ERROR: No protocol or filter specified")
        return {
            "status": "error",
            "message": "Protocol or pyshark_filter is required for this filter",
            "packets_filtered": 0
        }
    
    def filter_by_ip(self, arguments, analysis_data):
        """Filter packets by source IP address, optionally for a specific protocol."""
        source_ip_filter = arguments.get("source_ip")
        protocol_filter = arguments.get("protocol", "").lower()
        pyshark_filter = arguments.get("pyshark_filter", "").strip()
        
        print(f"[DEBUG] IP Filter - Input: source_ip={source_ip_filter}, protocol={protocol_filter}, pyshark_filter={pyshark_filter}")
        
        # If pyshark filter is provided, use it directly
        if pyshark_filter:
            print(f"[DEBUG] Using pyshark filter: {pyshark_filter}")
            return self.apply_pyshark_filter(pyshark_filter)
        
        if not source_ip_filter:
            print("[DEBUG] IP Filter - ERROR: No source IP specified")
            return {
                "status": "error",
                "message": "Source IP address is required for this filter",
                "packets_filtered": 0
            }
        
        # Build pyshark filter from IP and protocol
        filter_parts = [f"ip.src == {source_ip_filter}"]
        if protocol_filter:
            filter_parts.append(protocol_filter)
        
        constructed_filter = " and ".join(filter_parts)
        print(f"[DEBUG] Constructed pyshark filter: {constructed_filter}")
        
        return self.apply_pyshark_filter(constructed_filter)
    
    def filter_by_operation(self, arguments, analysis_data):
        """Filter packets by operation/procedure type using pyshark filter."""
        operation_filter = arguments.get("operation", "").lower()
        protocol_filter = arguments.get("protocol", "").lower()
        pyshark_filter = arguments.get("pyshark_filter", "").strip()
        
        print(f"[DEBUG] Operation Filter - Input: operation={operation_filter}, protocol={protocol_filter}, pyshark_filter={pyshark_filter}")
        
        # If pyshark filter is provided, use it directly
        if pyshark_filter:
            print(f"[DEBUG] Using provided pyshark filter: {pyshark_filter}")
            return self.apply_pyshark_filter(pyshark_filter)
        
        # Try to construct pyshark filter from operation and protocol
        if operation_filter and protocol_filter:
            # Map common operations to pyshark filters
            operation_mappings = {
                "nfs": {
                    "write": "nfs.procedure_v3 == 7",
                    "read": "nfs.procedure_v3 == 6", 
                    "create": "nfs.procedure_v3 == 8",
                    "lookup": "nfs.procedure_v3 == 3"
                },
                "smb2": {
                    "create": "smb2.cmd == 5",
                    "read": "smb2.cmd == 8",
                    "write": "smb2.cmd == 9",
                    "close": "smb2.cmd == 6",
                    "open": "smb2.cmd == 5"  # Same as create
                }
            }
            
            if protocol_filter in operation_mappings and operation_filter in operation_mappings[protocol_filter]:
                constructed_filter = operation_mappings[protocol_filter][operation_filter]
                print(f"[DEBUG] Constructed pyshark filter from operation mapping: {constructed_filter}")
                return self.apply_pyshark_filter(constructed_filter)
        
        print("[DEBUG] Operation Filter - ERROR: No pyshark filter provided and unable to construct from operation/protocol")
        return {
            "status": "error",
            "message": "pyshark_filter is required for operation filtering, or provide valid operation/protocol combination",
            "packets_filtered": 0
        }