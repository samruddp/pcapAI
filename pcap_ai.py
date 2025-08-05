"""
pcapAI - AI-Powered Network Packet Analysis Tool

Enhanced with Reinforcement Learning capabilities for continuous improvement
based on user feedback.

Enhanced Features (RL Branch):
- User feedback collection after each analysis
- Reinforcement learning model integration
- Response quality improvement over time
- Optional feedback skipping with --no-feedback flag
- Feedback statistics display

Original Features:
- PCAP file analysis using pyshark
- Natural language querying of network data
- NetApp LLM proxy API integration
- Offline fallback analysis mode

Usage:
    python pcap_ai.py --pcap file.pcap --key key.txt --query "question"
    python pcap_ai.py --pcap file.pcap --key key.txt --query "question" --no-feedback

Author: Enhanced for RL capabilities
Date: August 2025
"""

import argparse
import sys
from pcap_analyzer import PcapAnalyzer
from ai_query_handler import AIQueryHandler

def read_openai_key(key_file):
    """Read OpenAI API key from file."""
    try:
        with open(key_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: OpenAI key file '{key_file}' not found.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='AI-powered pcap file analyzer')
    parser.add_argument('--pcap', required=True, help='Path to pcap file')
    parser.add_argument('--key', required=True, help='Path to OpenAI API key file')
    parser.add_argument('--query', required=True, help='Question about the packet trace')
    parser.add_argument('--no-feedback', action='store_true', help='Skip feedback collection')
    
    args = parser.parse_args()
    
    # Read OpenAI API key
    openai_key = read_openai_key(args.key)
    
    # Initialize components
    pcap_analyzer = PcapAnalyzer(args.pcap)
    ai_handler = AIQueryHandler(openai_key)
    
    print(f"Analyzing pcap file: {args.pcap}")
    print(f"Query: {args.query}\n")
    
    try:
        # Analyze pcap file
        analysis_data = pcap_analyzer.analyze()
        
        # Get AI response
        response = ai_handler.query(args.query, analysis_data, args.pcap)
        
        print("AI Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Collect user feedback with improved input handling (unless disabled)
        if not args.no_feedback:
            try:
                import sys
                sys.stdout.flush()  # Ensure all output is displayed
                
                print("\nWould you like to provide feedback on this response?")
                collect_feedback = input("Enter 'y' for yes, or press Enter to skip: ").strip().lower()
                
                if collect_feedback == 'y':
                    ai_handler.collect_user_feedback()
                else:
                    print("Feedback skipped.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nFeedback collection skipped.")
            except Exception as e:
                print(f"Error during feedback prompt: {e}")
                print("You can provide feedback later using: python collect_feedback.py")
        else:
            print("\nFeedback collection disabled (use --no-feedback flag to skip)")
        
        # Show feedback statistics
        try:
            stats = ai_handler.feedback_handler.get_feedback_statistics()
            if stats["rated_sessions"] > 0:
                print(f"\nFeedback Statistics:")
                print(f"• Total sessions: {stats['total_sessions']}")
                print(f"• Rated sessions: {stats['rated_sessions']}")
                print(f"• Average rating: {stats['avg_rating']:.2f}/5.0")
        except Exception as e:
            print(f"Error displaying statistics: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
