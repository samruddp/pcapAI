import json
import os
from src.tools import Filter


class ToolFactory:
    """Factory class for managing and executing tools."""
    
    def __init__(self):
        self.filter = Filter()
    
    def get_tool_definitions(self):
        """Get OpenAI function definitions for all tools."""
        return self.filter.get_tool_definitions()
    
    def execute_tool(self, tool_name, arguments, analysis_data):
        """Execute a specific tool."""
        try:
            return self.filter.execute_tool(tool_name, arguments, analysis_data)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def list_available_tools(self):
        """List all available tools."""
        return ["filter_packets_by_protocol", "filter_packets_by_ip", "filter_packets_by_operation"]
