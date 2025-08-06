import argparse
import sys
import os
import json
import pickle
from src.pcap_analyzer import PcapAnalyzer
from src.ai_query_handler import AIQueryHandler

class SessionManager:
    """Manages session data for OpenAI key, pcap file, and parsed data."""
    def __init__(self):
        self.openai_key = None
        self.pcap_file = None
        self.parsed_data = None
        self.pcap_analyzer = None
        self.session_file = "session_data.pkl"
        self.load_session()

    def load_session(self):
        """Load session data from file if it exists."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'rb') as f:
                    data = pickle.load(f)
                    self.openai_key = data.get('openai_key')
                    self.pcap_file = data.get('pcap_file')
                    self.parsed_data = data.get('parsed_data')
                print("✓ Previous session loaded successfully")
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
            print("✓ Session saved successfully")
        except Exception as e:
            print(f"⚠️  Could not save session: {e}")

    def clear_session(self):
        """Clear current session and remove session file."""
        self.openai_key = None
        self.pcap_file = None
        self.parsed_data = None
        self.pcap_analyzer = None
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            print("✓ Session cleared successfully")
        except Exception as e:
            print(f"⚠️  Could not clear session file: {e}")

    def set_openai_key(self, key_file):
        """Set OpenAI API key."""
        try:
            with open(key_file, 'r') as f:
                self.openai_key = f.read().strip()
                print("✓ OpenAI key loaded successfully")
                self.save_session()
        except FileNotFoundError:
            print(f"Error: OpenAI key file '{key_file}' not found.")
            return False
        return True

    def set_pcap_file(self, pcap_file):
        """Set pcap file path and parse it."""
        if self.pcap_file == pcap_file and self.parsed_data is not None:
            print("✓ Using cached pcap data (already parsed)")
            return True
        
        self.pcap_file = pcap_file
        self.pcap_analyzer = PcapAnalyzer(pcap_file)
        
        print(f"📊 Parsing pcap file: {pcap_file}")
        print("⏳ This may take a moment for large files...")
        
        try:
            self.parsed_data = self.pcap_analyzer.parse_pcap()
            print("✓ Pcap file parsed successfully and cached for session")
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
        info = {
            'openai_key_set': self.openai_key is not None,
            'pcap_file': self.pcap_file,
            'pcap_parsed': self.parsed_data is not None,
            'data_size': len(str(self.parsed_data)) if self.parsed_data else 0
        }
        return info

# Global session manager
session = SessionManager()

def read_openai_key(key_file):
    """Read OpenAI API key from file."""
    try:
        with open(key_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: OpenAI key file '{key_file}' not found.")
        sys.exit(1)

def show_session_status():
    """Display current session status."""
    info = session.get_session_info()
    print("\n" + "="*50)
    print("📋 SESSION STATUS")
    print("="*50)
    print(f"🔑 OpenAI Key: {'✓ Set' if info['openai_key_set'] else '❌ Not set'}")
    print(f"📁 PCAP File: {info['pcap_file'] if info['pcap_file'] else '❌ Not set'}")
    print(f"📊 PCAP Parsed: {'✓ Yes' if info['pcap_parsed'] else '❌ No'}")
    if info['pcap_parsed']:
        print(f"💾 Data Size: {info['data_size']:,} characters")
    print("="*50 + "\n")

def show_help():
    """Show interactive mode help."""
    print("\n" + "="*60)
    print("🔧 INTERACTIVE MODE COMMANDS")
    print("="*60)
    print("📝 query <your question>     - Ask a question about the pcap")
    print("🔑 key <path>                - Set OpenAI API key file")
    print("📁 pcap <path>               - Set pcap file to analyze")
    print("📊 status                    - Show current session status")
    print("🔄 clear                     - Clear current session")
    print("❓ help                      - Show this help")
    print("🚪 quit/exit                 - Exit the program")
    print("="*60)
    print("💡 You can also just type your question directly!")
    print("="*60 + "\n")

def interactive_mode():
    """Run interactive session mode."""
    print("\n" + "🎯" + "="*58 + "🎯")
    print("  🤖 WELCOME TO PCAP AI INTERACTIVE SESSION! 🤖")
    print("🎯" + "="*58 + "🎯")
    print("💡 Type 'help' for commands or just ask questions about your pcap!")
    print("🚪 Type 'quit' or 'exit' to leave")
    
    show_session_status()
    
    while True:
        try:
            user_input = input("\n🤖 pcapAI> ").strip()
            
            if not user_input:
                continue
                
            # Handle exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using pcapAI! Session saved.")
                session.save_session()
                break
                
            # Handle help command
            elif user_input.lower() == 'help':
                show_help()
                continue
                
            # Handle status command
            elif user_input.lower() == 'status':
                show_session_status()
                continue
                
            # Handle clear command
            elif user_input.lower() == 'clear':
                session.clear_session()
                continue
                
            # Handle key command
            elif user_input.lower().startswith('key '):
                key_path = user_input[4:].strip().strip('"\'')
                if session.set_openai_key(key_path):
                    print("✓ API key updated in session")
                continue
                
            # Handle pcap command
            elif user_input.lower().startswith('pcap '):
                pcap_path = user_input[5:].strip().strip('"\'')
                if session.set_pcap_file(pcap_path):
                    print("✓ PCAP file updated in session")
                continue
                
            # Handle query command or direct question
            else:
                # Remove 'query ' prefix if present
                if user_input.lower().startswith('query '):
                    query = user_input[6:].strip()
                else:
                    query = user_input
                
                # Check if we have required data
                openai_key = session.get_openai_key()
                parsed_data = session.get_parsed_data()
                
                if not openai_key:
                    print("❌ No OpenAI API key set. Use: key <path_to_key_file>")
                    continue
                    
                if not parsed_data:
                    print("❌ No pcap data loaded. Use: pcap <path_to_pcap_file>")
                    continue
                
                # Process the query
                print(f"🤖 Processing: {query}")
                try:
                    ai_handler = AIQueryHandler(openai_key)
                    response = ai_handler.query(query, parsed_data)
                    
                    print("\n" + "="*50)
                    print("🤖 AI RESPONSE")
                    print("="*50)
                    print(response)
                    print("="*50)
                    
                except Exception as e:
                    print(f"❌ Error processing query: {e}")
                    
        except KeyboardInterrupt:
            print("\n👋 Session interrupted. Saving data...")
            session.save_session()
            break
        except EOFError:
            print("\n👋 Session ended. Saving data...")
            session.save_session()
            break

def main():
    parser = argparse.ArgumentParser(
        description='AI-powered pcap file analyzer with session management',
        epilog="""
Examples:
  # Interactive mode (recommended)
  python pcap_ai.py
  
  # Command-line mode
  python pcap_ai.py --key key.txt --pcap file.pcap --query "How many packets?"
  
  # Show session status
  python pcap_ai.py --status
  
  # Clear session
  python pcap_ai.py --clear
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--pcap', help='Path to pcap file (cached for session)')
    parser.add_argument('--key', help='Path to OpenAI API key file (cached for session)')
    parser.add_argument('--query', help='Question about the packet trace (single query mode)')
    parser.add_argument('--status', action='store_true', help='Show current session status')
    parser.add_argument('--clear', action='store_true', help='Clear current session')
    parser.add_argument('--interactive', '-i', action='store_true', help='Force interactive mode')
    
    args = parser.parse_args()
    
    # Handle clear request
    if args.clear:
        session.clear_session()
        return
    
    # Handle status request
    if args.status:
        show_session_status()
        return
    
    # Set OpenAI key if provided
    if args.key:
        if not session.set_openai_key(args.key):
            print("❌ Failed to set API key")
            return
    
    # Set pcap file if provided
    if args.pcap:
        if not session.set_pcap_file(args.pcap):
            print("❌ Failed to set PCAP file")
            return
    
    # If query is provided, run single query mode
    if args.query:
        # Get session data
        openai_key = session.get_openai_key()
        parsed_data = session.get_parsed_data()
        
        if not openai_key:
            print("❌ Error: OpenAI key not set for this session.")
            print("💡 Use --key to set the OpenAI key file")
            return
            
        if not parsed_data:
            print("❌ Error: No pcap data available.")
            print("💡 Use --pcap to set the pcap file")
            return
        
        # Initialize AI handler and process query
        ai_handler = AIQueryHandler(openai_key)
        print(f"🤖 Processing query: {args.query}")
        
        try:
            response = ai_handler.query(args.query, parsed_data)
            
            print("\n" + "="*50)
            print("🤖 AI RESPONSE")
            print("="*50)
            print(response)
            print("="*50)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    
    # If no query provided or interactive flag set, start interactive mode
    else:
        interactive_mode()

if __name__ == "__main__":
    main()