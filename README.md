# pcapAI
august 2025 hackathon project repository

An AI-powered command line tool for analyzing network packet captures (pcap files) using natural language queries.

## Features
- Parse pcap files using pyshark
- Ask questions about packet traces in plain English
- Get AI-powered answers using NetApp's internal LLM proxy API
- Command line interface for easy usage
- Offline mode fallback when AI is unavailable

## Prerequisites
- Python 3.7+
- Git (for version control)
- Wireshark/tshark installed (required by pyshark)
- NetApp LLM proxy API key
- Access to NetApp internal network

## Installation

### 1. Install Git
Download and install Git from: https://git-scm.com/download/windows
- Choose "Git from the command line and also from 3rd-party software" during installation
- Restart your terminal/PowerShell after installation

### 2. Verify Git Installation
```bash
git --version
```

### 3. Configure Git (first time setup)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage
```bash
python pcap_ai.py --pcap sample.pcap --key netapp_llm_key.txt --query "What protocols are used in this trace?"
```

## API Configuration
This tool uses NetApp's internal LLM proxy API:
- Base URL: https://llm-proxy-api.ai.eng.netapp.com
- Model: gpt-4o
- Requires valid NetApp API key

### Troubleshooting SSL Certificate Errors
If you encounter SSL certificate verification errors, follow the troubleshooting guide at:
https://llm-proxy-web.ai.eng.netapp.com/Troubleshooting

## Requirements
- Python 3.7+
- NetApp LLM proxy API key
- Wireshark/tshark installed (required by pyshark)
- Access to NetApp internal network
