import argparse
import sys
import os
import json
from datetime import datetime
from src.session_manager import SessionManager

# Global session manager (will be initialized in main)
session = None

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
    print(f"🤖 AI Handler: {'✓ Ready' if info['ai_handler_ready'] else '❌ Not ready'}")
    print(
        f"🔧 Protocol Filter: {', '.join(info['protocol_filter']) if info['protocol_filter'] else 'None (all protocols)'}"
    )
    print(f"📦 Filtered Packets: {info['filtered_packets_count']:,}")
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
    print("🎯 MODE INFORMATION")
    print("="*60)
    print("🧪 TEST MODE (--t)           - Collects feedback after each AI response")
    print("                             - Prompts for satisfaction rating & reason")
    print("                             - Used for improving AI model performance")
    print("                             - Saves feedback to dataset.json")
    print("👤 USER MODE (--u)           - Standard mode")
    print("="*60)
    print("💡 You can also just type your question directly!")
    print("="*60 + "\n")

def interactive_mode(test_mode=False):
    """Run interactive session mode."""
    print("\n" + "🎯" + "="*58 + "🎯")
    if test_mode:
        print("  🧪 PCAP AI TEST MODE - WITH FEEDBACK🧪")
    else:
        print("  🤖 WELCOME TO PCAP AI INTERACTIVE SESSION! 🤖")
    print("🎯" + "="*58 + "🎯")
    print("💡 Type 'help' for commands or just ask questions about your pcap!")
    print("🚪 Type 'quit' or 'exit' to leave")
    
    # Only show session status in test mode
    if test_mode:
        show_session_status()

    # Prompt for a single protocol once per session
    known_protocols = ["NFS", "HTTP", "SMB2"]
    print("🧬 Available protocols:", ", ".join(known_protocols))
    
    while True:
        proto_input = input("🌈 Please enter ONE protocol to focus on for this session (or press Enter to skip): ").strip().upper()
        
        if not proto_input:
            session.last_protocols = []
            print("✨ No protocol filter set. All protocols will be considered.")
            break
        elif proto_input in known_protocols:
            session.last_protocols = [proto_input]
            print(f"✅ Protocol set for session: {proto_input}")
            break
        else:
            print(f"❌ '{proto_input}' is not a valid protocol. Please choose from: {', '.join(known_protocols)}")
            # The loop will continue and ask for input again

    # Set protocol filter once (this will filter packets once)
    if session.get_parsed_data():
        session.set_protocol_filter(session.last_protocols)

    while True:
        try:
            # if last_protocol is not set, ask the user for protocol input and filter again
            if not session.last_protocols:
                proto_input = (
                    input("🌈 Please enter ONE protocol to focus on for this session: ")
                    .strip()
                    .upper()
                )
                if proto_input in known_protocols:
                    session.last_protocols = [proto_input]
                    session.set_protocol_filter(session.last_protocols)
                    print(f"✅ Protocol set for session: {proto_input}")
                else:
                    print(
                        f"❌ '{proto_input}' is not a valid protocol. Please choose from: {', '.join(known_protocols)}"
                    )
                    continue

            user_input = input("\n🤖 pcapAI> ").strip()
            
            if not user_input:
                continue
                
            # Handle exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using pcapAI! Session saved.")
                session.save_session()
                session.save_history_and_dataset()
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
                    # Re-filter packets with current protocol
                    session.set_protocol_filter(session.last_protocols)
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
                if test_mode:
                    print(f"🤖 Processing: {query}")
                else:
                    print("🤖 Processing...")
                try:
                    # Get cached AI handler and filtered data
                    ai_handler = session.get_ai_handler()
                    if not ai_handler:
                        print("❌ Failed to initialize AI handler")
                        continue

                    filtered_packets, analysis_data = session.get_filtered_data()
                    if filtered_packets is None:
                        print("❌ No filtered packet data available")
                        continue

                    if test_mode:
                        print(f"🔎 Analysing {len(filtered_packets)} packets...")                    

                    response = ai_handler.query(query, analysis_data, session.conversation_history)
                    
                    print("\n" + "="*50)
                    print("🤖 AI RESPONSE")
                    print("="*50)
                    print(response)
                    print("="*50)
                    
                    # In test mode, collect feedback
                    if test_mode:
                        # Get feedback rating
                        while True:
                            try:
                                feedback = input("\n📊 Rate the AI's response [s=satisfied | n=neutral | u=unsatisfied]: ").strip().lower()
                                if feedback in ['satisfied', 'neutral', 'unsatisfied', 's', 'n', 'u']:
                                    # Normalize to full words
                                    if feedback in ['s', 'satisfied']:
                                        feedback = 'satisfied'
                                    elif feedback in ['n', 'neutral']:
                                        feedback = 'neutral'
                                    elif feedback in ['u', 'unsatisfied']:
                                        feedback = 'unsatisfied'
                                    break
                                else:
                                    print("❌ Please respond with 'satisfied', 'neutral', or 'unsatisfied'")
                            except ValueError:
                                print("❌ Please enter a valid response (satisfied/neutral/unsatisfied)")
                        
                        # Ask for optional reason
                        reason = ""
                        try:
                            reason_input = input("\n💭 Would you like to provide a reason for your rating? (If not, then press Enter to skip): ").strip()
                            if reason_input:
                                reason = reason_input
                        except (KeyboardInterrupt, EOFError):
                            reason = ""
                        
                        print(f"✓ Thank you for your feedback! Rating: {feedback}")
                        
                        # Update history and dataset with feedback
                        session.history.append({
                            "session_id": session.session_id,
                            "timestamp": datetime.now().isoformat(),
                            "user_details": session.user_details,
                            "pcap_file": session.pcap_file,
                            "query": query,
                            "response": response,
                            "test_mode": True,
                            "feedback": {
                                "rating": feedback,
                                "reason": reason
                            }
                        })
                        session.dataset.append({
                            "query": query, 
                            "response": response,
                            "feedback": {
                                "rating": feedback,
                                "reason": reason
                            }
                        })
                        session.conversation_history.append({
                            "query": query,
                            "response": response
                        })
                    else:
                        # Update history and dataset without feedback
                        session.history.append({
                            "session_id": session.session_id,
                            "timestamp": datetime.now().isoformat(),
                            "user_details": session.user_details,
                            "pcap_file": session.pcap_file,
                            "query": query,
                            "response": response,
                            "test_mode": False
                        })
                        session.dataset.append({"query": query, "response": response})
                        session.conversation_history.append({
                            "query": query,
                            "response": response
                        })
                    
                except Exception as e:
                    print(f"❌ Error processing query: {e}")
                    
        except KeyboardInterrupt:
            print("\n👋 Session interrupted. Saving data...")
            session.save_session()
            session.save_history_and_dataset()
            break
        except EOFError:
            print("\n👋 Session ended. Saving data...")
            session.save_session()
            session.save_history_and_dataset()
            break

def main():
    parser = argparse.ArgumentParser(
        description='AI-powered pcap file analyzer with session management',
        epilog="""
Examples:
  # User mode
  python pcap_ai.py --key key.txt --pcap file.pcap --u
  
  # Test mode
  python pcap_ai.py --key key.txt --pcap file.pcap --t
  
  # Show session status
  python pcap_Interactive mode (recommended)
  python pcap_ai.py
  
  # Clear session
  python pcap_ai.py --clear
  
  # Clear history
  python pcap_ai.py --clear-history
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--pcap', help='Path to pcap file (cached for session)')
    parser.add_argument('--key', help='Path to OpenAI API key file (cached for session)')
    parser.add_argument('--status', action='store_true', help='Show current session status')
    parser.add_argument('--clear', action='store_true', help='Clear current session')
    parser.add_argument('--clear-history', action='store_true', help='Clear the history file')
    parser.add_argument('--interactive', '-i', action='store_true', help='Force interactive mode')
    parser.add_argument('--t', action='store_true', help='Run in test mode')
    parser.add_argument('--u', action='store_true', help='Run in user mode')
    
    args = parser.parse_args()
    
    # Check that either test mode or user mode is specified
    if not args.t and not args.u:
        print("❌ Error: You must specify either test mode (--t) or user mode (--u)")
        print("\nExamples:")
        print("  python3 pcap_ai.py --t --pcap file.pcap --key key.txt")
        print("  python3 pcap_ai.py --u --pcap file.pcap --key key.txt")
        return
    
    # Ensure only one mode is specified
    if args.t and args.u:
        print("❌ Error: Cannot specify both test mode (--t) and user mode (--u) at the same time")
        print("Please choose either test mode (--t) or user mode (--u)")
        return
    
    # Debug: Show which mode we're in
    if args.t:
        print("🧪 DEBUG: Running in TEST MODE")
    
    # Initialize the global session with the correct mode
    global session
    session = SessionManager(test_mode=args.t)
    
    # Handle clear-history request
    if args.clear_history:
        history_file = ".cache/history.json"
        try:
            with open(history_file, "w") as file:
                json.dump([], file, indent=4)
            print("✓ History cleared successfully")
        except Exception as e:
            print(f"⚠️  Could not clear history: {e}")
        return
    
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
    
    # Start interactive mode
    interactive_mode(test_mode=args.t)

if __name__ == "__main__":
    main()