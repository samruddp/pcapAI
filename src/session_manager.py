"""
Session Manager for pcapAI - Manages session data, history, and AI handler caching
"""
import json
import pickle
import uuid
import getpass
import os
from src.pcap_analyzer import PcapAnalyzer
from src.ai_query_handler import AIQueryHandler
from src.tool_calling_handler import ToolCallingHandler
from src.protocols.nfs import NFSProtocol
from src.protocols.smb import SMBProtocol
from src.protocols.http import HTTPProtocol

protocol_classes = {
    "NFS": NFSProtocol(),
    "SMB": SMBProtocol(),
    "HTTP": HTTPProtocol(),
    # Add more as needed
}


class SessionManager:
    """Manages session data for OpenAI key, pcap file, parsed data, history, and dataset."""
    def __init__(self, test_mode=False):
        self.test_mode = test_mode  # Store the mode for verbose output control
        self.openai_key = None
        self.pcap_file = None
        self.parsed_data = None
        self.pcap_analyzer = None
        self.ai_handler = None  # Cache AI handler
        self.filtered_packets = None  # Cache filtered packets
        self.analysis_data = None  # Cache analysis data
        self.last_protocols = []  # Track current protocol filter
        self.session_file = "session_data.pkl"
        self.history_file = ".cache/history.json"
        self.dataset_file = "dataset.json" 
        self.history = []
        self.dataset = []
        self.conversation_history = []  # <-- add this for AI context
        self.session_id = str(uuid.uuid4())  # Generate a unique session ID
        self.user_details = self.get_user_details()  # Capture user details
        self.load_session()
        self.load_history_and_dataset()

    def get_user_details(self):
        """Capture user details with platform info."""
        import platform

        system = platform.system()

        try:
            username = getpass.getuser()
            hostname = platform.node()

            details = {
                "username": username,
                "hostname": hostname,
                "platform": system,
                "platform_release": platform.release(),
                "python_version": platform.python_version(),
            }

            self.log_debug(f"✓ Running on {system}")
            return details

        except Exception as e:
            return {
                "username": "unknown",
                "hostname": "unknown",
                "platform": system,
                "error": str(e),
            }

    def log_debug(self, message):
        """Print debug messages only in test mode."""
        if self.test_mode:
            print(message)

    def load_session(self):
        """Load session data from file if it exists."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'rb') as f:
                    data = pickle.load(f)
                    self.openai_key = data.get('openai_key')
                    self.pcap_file = data.get('pcap_file')
                    self.parsed_data = data.get('parsed_data')
                self.log_debug("✓ Previous session loaded successfully")
        except Exception as e:
            print(f"⚠️  Could not load previous session: {e}")

    def save_session(self):
        """Save current session data to file."""
        try:
            data = {
                'openai_key': self.openai_key,
                'pcap_file': self.pcap_file,
                'parsed_data': self.parsed_data
            }
            with open(self.session_file, 'wb') as f:
                pickle.dump(data, f)
            self.log_debug("✓ Session saved successfully")
        except Exception as e:
            print(f"⚠️  Could not save session: {e}")

    def clear_session(self):
        """Clear current session and remove session file."""
        # self.openai_key = None
        # self.pcap_file = None
        # self.parsed_data = None
        # self.pcap_analyzer = None
        # self.ai_handler = None  # Clear cached AI handler
        self.filtered_packets = None  # Clear cached filtered packets
        self.analysis_data = None  # Clear cached analysis data
        self.last_protocols = []  # Clear protocol filter
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            self.log_debug("✓ Session cleared successfully")
        except Exception as e:
            print(f"⚠️  Could not clear session file: {e}")

    def set_openai_key(self, key_file):
        """Set OpenAI API key and initialize AI handler."""
        try:
            with open(key_file, 'r') as f:
                self.openai_key = f.read().strip()
                # Initialize AI handler once when key is set
                self._initialize_ai_handler(test_mode=self.test_mode)
                self.log_debug("✓ OpenAI key loaded successfully")
                self.save_session()
        except FileNotFoundError:
            print(f"Error: OpenAI key file '{key_file}' not found.")
            return False
        return True

    def _initialize_ai_handler(self, test_mode=None):
        """Initialize AI handler once when we have the key. Choose handler based on PCAP file size."""
        if self.openai_key:
            try:
                # Check if we have a PCAP file and get its size
                file_size_kb = 0
                handler_type = "standard"
                
                if self.pcap_file and os.path.exists(self.pcap_file):
                    file_size_bytes = os.path.getsize(self.pcap_file)
                    file_size_kb = file_size_bytes / 1024
                    
                    if file_size_kb > 10:  # 50 KB threshold
                        handler_type = "tool_calling"
                        print(f"🔧 Initializing Tool Calling AI handler (PCAP size: {file_size_kb:.1f} KB > 50 KB)...")
                        self.ai_handler = ToolCallingHandler(self.openai_key, test_mode=test_mode or self.test_mode)
                        print("✓ Tool Calling AI handler initialized and cached for session")
                    else:
                        print(f"🔧 Initializing standard AI handler (PCAP size: {file_size_kb:.1f} KB ≤ 50 KB)...")
                        self.ai_handler = AIQueryHandler(self.openai_key, test_mode=test_mode or self.test_mode)
                        print("✓ Standard AI handler initialized and cached for session")
                else:
                    # No PCAP file yet, use standard handler
                    print("🔧 Initializing standard AI handler (no PCAP file yet)...")
                    self.ai_handler = AIQueryHandler(self.openai_key, test_mode=test_mode or self.test_mode)
                    print("✓ Standard AI handler initialized and cached for session")
                    
            except Exception as e:
                print(f"⚠️  Error initializing AI handler: {e}")
                self.ai_handler = None

    def set_protocol_filter(self, protocols):
        """Set protocol filter and process packets once."""
        if self.last_protocols == protocols and self.filtered_packets is not None:
            print("✓ Using cached filtered packets (protocol unchanged)")
            return True

        self.last_protocols = protocols

        if not self.parsed_data:
            print("❌ No PCAP data available to filter")
            return False

        try:
            print(f"🔄 Filtering packets for protocol(s): {protocols}")

            # Parse the data if it's a string
            if isinstance(self.parsed_data, str):
                parsed_data = json.loads(self.parsed_data)
            else:
                parsed_data = self.parsed_data

            packets = (
                parsed_data
                if isinstance(parsed_data, list)
                else parsed_data.get("packets", [])
            )

            if protocols:
                proto_name = protocols[0]  # Use first protocol
                proto_handler = protocol_classes.get(proto_name)
                if proto_handler:
                    self.filtered_packets = proto_handler.filter_packets(self.pcap_file)
                    self.analysis_data = proto_handler.analyze(self.filtered_packets)
                    print(
                        f"✓ Filtered to {len(self.filtered_packets)} {proto_name} packets"
                    )
                else:
                    print(
                        f"❌ Protocol handler for {proto_name} not found. Using all packets."
                    )
                    self.filtered_packets = packets
                    self.analysis_data = {"packets": self.filtered_packets}
            else:
                self.filtered_packets = packets
                self.analysis_data = {"packets": self.filtered_packets}
                print(
                    f"✓ Using all {len(self.filtered_packets)} packets (no protocol filter)"
                )

            return True

        except Exception as e:
            print(f"❌ Error filtering packets: {e}")
            return False

    def get_ai_handler(self):
        """Get the cached AI handler."""
        if not self.ai_handler and self.openai_key:
            self._initialize_ai_handler()
        return self.ai_handler

    def get_filtered_data(self):
        """Get the cached filtered packets and analysis data."""
        return self.filtered_packets, self.analysis_data

    def set_pcap_file(self, pcap_file):
        """Set pcap file path and parse it."""
        if self.pcap_file == pcap_file and self.parsed_data is not None:
            self.log_debug("✓ Using cached pcap data (already parsed)")
            return True
        
        self.pcap_file = pcap_file
        self.pcap_analyzer = PcapAnalyzer(pcap_file)
        
        print(f"📊 Parsing pcap file: {pcap_file}")
        print("⏳ This may take a moment for large files...")
        
        try:
            self.parsed_data = self.pcap_analyzer.parse_pcap()
            self.log_debug("✓ Pcap file parsed successfully and cached for session")
            
            # Reinitialize AI handler based on new file size
            if self.openai_key:
                self.ai_handler = None  # Clear existing handler
                self._initialize_ai_handler()
            
            self.save_session()
            return True
        except Exception as e:
            print(f"❌ Error parsing pcap file: {e}")
            return False

    def get_openai_key(self):
        """Get OpenAI API key."""
        if not self.openai_key:
            return None
        return self.openai_key

    def get_parsed_data(self):
        """Get parsed pcap data."""
        if not self.parsed_data:
            return None
        return self.parsed_data

    def get_session_info(self):
        """Get current session information."""
        # Determine AI handler type
        ai_handler_type = "None"
        if self.ai_handler:
            if hasattr(self.ai_handler, '__class__'):
                ai_handler_type = "Tool Calling" if "ToolCalling" in self.ai_handler.__class__.__name__ else "Standard"
        
        # Get file size if available
        file_size_kb = 0
        if self.pcap_file and os.path.exists(self.pcap_file):
            file_size_bytes = os.path.getsize(self.pcap_file)
            file_size_kb = file_size_bytes / 1024
        
        info = {
            "openai_key_set": self.openai_key is not None,
            "pcap_file": self.pcap_file,
            "pcap_parsed": self.parsed_data is not None,
            "ai_handler_ready": self.ai_handler is not None,
            "ai_handler_type": ai_handler_type,
            "file_size_kb": file_size_kb,
            "protocol_filter": self.last_protocols,
            "filtered_packets_count": len(self.filtered_packets)
            if self.filtered_packets
            else 0,
            "data_size": len(str(self.parsed_data)) if self.parsed_data else 0,
        }
        return info

    def load_history_and_dataset(self):
        """Load history.json and dataset.json into memory."""
        # Ensure the .cache directory exists
        cache_dir = ".cache"
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Load history.json
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as file:
                    self.history = json.load(file)
                    self.log_debug("✓ History loaded successfully")
            except json.JSONDecodeError:
                print("⚠️  Invalid JSON in history.json. Starting with an empty history.")
                self.history = []

        # Load dataset.json
        if os.path.exists(self.dataset_file):
            try:
                with open(self.dataset_file, "r") as file:
                    self.dataset = json.load(file)
                    self.log_debug("✓ Dataset loaded successfully")
            except json.JSONDecodeError:
                print("⚠️  Invalid JSON in dataset.json. Starting with an empty dataset.")
                self.dataset = []

    def save_history_and_dataset(self):
        """Save history.json and dataset.json from memory to disk."""
        try:
            # Save history.json in the .cache directory
            with open(self.history_file, "w") as file:
                json.dump(self.history, file, indent=4)
            self.log_debug("✓ History saved successfully")
        except Exception as e:
            print(f"⚠️  Could not save history.json: {e}")

        try:
            # Save dataset.json in the main folder
            with open(self.dataset_file, "w") as file:
                json.dump(self.dataset, file, indent=4)
            self.log_debug("✓ Dataset saved successfully")
        except Exception as e:
            print(f"⚠️  Could not save dataset.json: {e}")
