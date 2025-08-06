# pcapAI 🤖
August 2025 hackathon project

AI-powered network packet capture analysis with **persistent interactive sessions** and natural language queries.

## 🚀 Key Features
- **Interactive Session Management**: Set your API key and pcap file once, query multiple times
- **Persistent Data Storage**: Your session data survives between program restarts
- **Smart Caching**: Large pcap files are parsed once and cached for performance
- **Natural Language Queries**: Ask questions about packet traces in plain English
- **Dual Operation Modes**: Interactive mode for exploration, CLI mode for automation
- **AI-Powered Analysis**: Uses NetApp's internal LLM proxy API for intelligent responses
- **Offline Fallback**: Graceful handling when AI is unavailable

## 🎯 Quick Start

### 1. **First Time Setup** (One-time only)
```bash
# Set your API key and pcap file once
python pcap_ai.py --key "path/to/your/netapp_llm_key.txt" --pcap "path/to/your/file.pcap"
```
This automatically enters **interactive mode** after setup.

### 2. **Interactive Session** (Recommended)
```bash
🤖 pcapAI> How many packets are in this capture?
🤖 pcapAI> What are the top source IP addresses?
🤖 pcapAI> Show me any suspicious network activity
🤖 pcapAI> quit
```

### 3. **Future Sessions** (No setup needed!)
```bash
# Just run - your previous session is automatically restored!
python pcap_ai.py
🤖 pcapAI> What protocols are being used?
🤖 pcapAI> Analyze the bandwidth usage patterns
```

### 4. **Quick Single Query** (Automation friendly)
```bash
python pcap_ai.py --query "What ports are being used most frequently?"
```

## 📋 Interactive Commands

| Command | Description | Example |
|---------|-------------|---------|
| `<question>` | Ask any question about your pcap | `How many HTTP requests are there?` |
| `key <path>` | Update API key file | `key /path/to/new/key.txt` |
| `pcap <path>` | Load new pcap file | `pcap /path/to/new/file.pcap` |
| `status` | Show current session info | `status` |
| `clear` | Clear all session data | `clear` |
| `help` | Show all commands | `help` |
| `quit` or `exit` | Save session and exit | `quit` |

## 🛠️ Advanced Usage

### **Session Management**
```bash
# Check what's currently loaded
python pcap_ai.py --status

# Clear your session and start fresh
python pcap_ai.py --clear

# Force interactive mode
python pcap_ai.py --interactive
```

### **Workflow Examples**

#### **🔍 Security Analysis Workflow**
```bash
python pcap_ai.py --key api_key.txt --pcap suspicious_traffic.pcap
🤖 pcapAI> Are there any port scans in this traffic?
🤖 pcapAI> Show me connections to external IP addresses
🤖 pcapAI> What's the timeline of network events?
🤖 pcapAI> Are there any DNS exfiltration attempts?
```

#### **📊 Performance Analysis Workflow**
```bash
python pcap_ai.py
🤖 pcapAI> pcap network_performance.pcap
🤖 pcapAI> What's the bandwidth utilization over time?
🤖 pcapAI> Show me the largest packets and their sources
🤖 pcapAI> Are there any retransmissions or packet loss?
```

#### **🕵️ Network Forensics Workflow**
```bash
python pcap_ai.py
🤖 pcapAI> What applications are generating traffic?
🤖 pcapAI> Show me the communication patterns
🤖 pcapAI> Are there any unusual protocols being used?
🤖 pcapAI> What's the geographic distribution of traffic?
```

## 💡 Example Queries

### **General Analysis**
- "How many packets are in this capture?"
- "What's the time span of this network trace?"
- "Show me the protocol distribution"
- "What are the top talkers by data volume?"

### **Security Focused**
- "Are there any suspicious network connections?"
- "Show me failed connection attempts"
- "Are there any port scans or brute force attempts?"
- "What external IP addresses are being contacted?"

### **Performance Analysis** 
- "What's the bandwidth usage pattern?"
- "Show me the largest packets and their purpose"
- "Are there any network errors or retransmissions?"
- "What's the latency between specific hosts?"

### **Application Layer**
- "What web traffic is present in this capture?"
- "Show me DNS queries and responses"
- "Are there any file transfers happening?"
- "What applications are generating the most traffic?"

## 🏗️ Project Structure
```
pcapAI/
├── src/
│   ├── __init__.py
│   ├── pcap_analyzer.py      # Packet parsing and analysis
│   ├── ai_query_handler.py   # AI API integration
│   └── packet_parser.py      # Core packet processing
├── pcap_ai.py               # Main entry point with session management
├── session_data.pkl         # Auto-generated session storage
├── requirements.txt         # Python dependencies
├── .gitignore              # Excludes session and key files
└── README.md               # This file
```

## 🔧 Installation & Setup

### **Prerequisites**
- Python 3.7+
- Git (for version control)
- Wireshark/tshark installed (required by pyshark)
- NetApp LLM proxy API key
- Access to NetApp internal network

### **1. Install Git**
Download and install Git from: https://git-scm.com/download/windows
- Choose "Git from the command line and also from 3rd-party software" during installation
- Restart your terminal/PowerShell after installation

### **2. Verify Git Installation**
```bash
git --version
```

### **3. Configure Git** (first time setup)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### **4. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

## 🔑 API Configuration
This tool uses NetApp's internal LLM proxy API:
- **Base URL**: https://llm-proxy-api.ai.eng.netapp.com
- **Model**: gpt-4o
- **Requires**: Valid NetApp API key file

### **Troubleshooting SSL Certificate Errors**
If you encounter SSL certificate verification errors, follow the troubleshooting guide at:
https://llm-proxy-web.ai.eng.netapp.com/Troubleshooting

## 🚀 Performance Benefits

### **Before (Traditional CLI)**
```bash
$ python pcap_ai.py --key key.txt --pcap large_file.pcap --query "Question 1"
# ⏳ Parsing 500MB pcap file... (2 minutes)
$ python pcap_ai.py --key key.txt --pcap large_file.pcap --query "Question 2"  
# ⏳ Re-parsing same file... (2 minutes again!)
```

### **After (Interactive Session)**
```bash
$ python pcap_ai.py --key key.txt --pcap large_file.pcap
# ⏳ Parsing 500MB pcap file... (2 minutes, one time only)
🤖 pcapAI> Question 1  # ⚡ Instant response!
🤖 pcapAI> Question 2  # ⚡ Instant response!
🤖 pcapAI> Question 3  # ⚡ Instant response!

# Next day...
$ python pcap_ai.py
🤖 pcapAI> New question  # ⚡ Everything restored instantly!
```

## 📊 Session Persistence

Your session data automatically persists:
- ✅ **API Key**: Set once, use forever
- ✅ **Parsed PCAP Data**: Large files cached indefinitely  
- ✅ **File Paths**: Remembers your last pcap file
- ✅ **Performance**: No re-parsing on restart

## 🛡️ Security & Privacy

- Session files (`session_data.pkl`) are automatically excluded from git
- API key files are ignored by `.gitignore`
- No sensitive data is transmitted except through NetApp's secure API
- Session data is stored locally only

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Test with various pcap files
4. Submit a pull request

## 📝 Requirements
- Python 3.7+
- NetApp LLM proxy API key
- Wireshark/tshark installed (required by pyshark)
- Access to NetApp internal network

---

**🎉 Happy Network Analysis!** 

For questions or issues, please create an issue in the repository or contact the development team.
