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

### Basic Usage
```bash
python pcap_ai.py --pcap "testpcap1.pcap" --key "openai_key.txt" --query "What protocols are used in this trace?"
```

### Usage with Feedback Collection (Reinforcement Learning)
```bash
# Run with feedback collection enabled (default)
python pcap_ai.py --pcap "testpcap1.pcap" --key "openai_key.txt" --query "What protocols are used in this trace?"

# Skip feedback collection
python pcap_ai.py --pcap "testpcap1.pcap" --key "openai_key.txt" --query "What protocols are used in this trace?" --no-feedback
```

### Standalone Feedback Collection
If you need to provide feedback for a previous session:
```bash
python collect_feedback.py
```

### Model Training and Statistics
```bash
# View feedback statistics and train the model
python train_model.py --show-stats

# Train model without showing statistics
python train_model.py
```

### Example Queries
```bash
# Protocol analysis
python pcap_ai.py --pcap "capture.pcap" --key "openai_key.txt" --query "What protocols are used in this trace?"

# Traffic analysis
python pcap_ai.py --pcap "capture.pcap" --key "openai_key.txt" --query "What is the most active IP address?"

# Security analysis
python pcap_ai.py --pcap "capture.pcap" --key "openai_key.txt" --query "Are there any suspicious activities in this traffic?"
```

## Reinforcement Learning Features

This tool includes reinforcement learning capabilities that improve responses based on user feedback:

- **Feedback Collection**: Rate responses (1-5 stars) and provide comments
- **Response Enhancement**: AI learns from feedback to improve future responses
- **Pattern Learning**: Adapts to user preferences for different query types
- **Continuous Improvement**: Model automatically updates as feedback is collected

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
- Additional Python packages: numpy, scikit-learn (for RL features)

## Project Structure
```
pcapAI/
├── pcap_ai.py              # Main application script
├── pcap_analyzer.py        # PCAP file analysis module
├── ai_query_handler.py     # AI query processing with RL integration
├── feedback_handler.py     # User feedback collection and storage
├── rl_trainer.py          # Reinforcement learning trainer
├── train_model.py         # Model training script
├── collect_feedback.py    # Standalone feedback collection
├── requirements.txt       # Python dependencies
├── rl_config.json        # RL configuration settings
└── README.md             # This file
```

## Generated Files
During usage, the following files will be created:
- `feedback_data.json` - Stores user feedback and session data
- `rl_model.pkl` - Trained reinforcement learning model
