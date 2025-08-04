# pcapAI
august 2025 hackathon project repository

An AI-powered command line tool for analyzing network packet captures (pcap files) using natural language queries.

## Features
- Parse pcap files using pyshark
- Ask questions about packet traces in plain English
- Get AI-powered answers using OpenAI GPT
- Command line interface for easy usage

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python pcap_ai.py --pcap sample.pcap --key openai_key.txt --query "What protocols are used in this trace?"
```

## Requirements
- Python 3.7+
- OpenAI API key
- Wireshark/tshark installed (required by pyshark)
