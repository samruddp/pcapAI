import argparse
import sys
from src.pcap_analyzer import PcapAnalyzer
from src.ai_query_handler import AIQueryHandler

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
    
    args = parser.parse_args()
    
    # Read OpenAI API key
    openai_key = read_openai_key(args.key)
    
    # Initialize components
    pcap_analyzer = PcapAnalyzer(args.pcap)
    ai_handler = AIQueryHandler(openai_key)
    
    print(f"Analyzing pcap file: {args.pcap}")
    print(f"Query: {args.query}\n")
    
    try:
        # Parse pcap file
        parsed_data = pcap_analyzer.parse_pcap()
        print("Pcap file parsed successfully.")
        # Analyze pcap file
        # analysis_data = pcap_analyzer.analyze()
        
        # Get AI response
        response = ai_handler.query(args.query, parsed_data)
        
        print("AI Response:")
        print("-" * 50)
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
