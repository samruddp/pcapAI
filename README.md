# PacketSense 🤖
August 2025 hackathon project

AI-powered network packet capture analysis with **natural language queries** and **persistent interactive sessions**.

## 🚀 Key Features
- **Natural Language Queries**: Ask questions about packet traces in plain English
- **AI-Powered Analysis**: Uses NetApp's internal LLM proxy API for intelligent responses
- **Interactive Session Management**: Set your API key and pcap file once, query multiple times
- **Persistent Data Storage**: Your session data survives between program restarts
- **Protocol Filtering**: Focus analysis on specific protocols (NFS, SMB2, HTTP) per session
- **AI Tool Calling**: Advanced filtering with pyshark integration for precise packet analysis
- **Dual Operation Modes**: Interactive mode with two flavors : User mode and Test mode (Feedback collection)

## 🎯 Quick Start

### 1. **First Time Setup** (One-time only)

#### **User Mode**
```bash
# Set your API key and pcap file once (User mode)
python pcap_ai.py --key /path/to/your/netapp_llm_key.txt --pcap /path/to/your/file.pcap --u
```

#### **Test Mode**
```bash
# Set your API key and pcap file once (Test mode for feedback collection)
python pcap_ai.py --key /path/to/your/netapp_llm_key.txt --pcap /path/to/your/file.pcap --t
```
This automatically enters **interactive mode** after setup in either mode.

### 3. **Protocol Selection** (Required per session)
```bash
🧬 Available protocols: NFS, HTTP, SMB2
🌈 Please enter ONE protocol to focus on for this session (or press Enter to skip): NFS
✅ Protocol set for session: NFS
```
 
### 4. **Interactive Session** (Both modes)
```bash
🤖 packetSense> How many packets are in this capture?
🤖 packetSense> What are the top source IP addresses?
🤖 packetSense> quit
```
 
### 5. **Test Mode Feedback** (Test mode only)
```bash
📊 Rate the AI's response [s=satisfied | n=neutral | u=unsatisfied]: s
💭 Would you like to provide a reason for your rating? (If not, then press Enter to skip): The analysis was comprehensive and accurate
✓ Thank you for your feedback! Rating: satisfied
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
 
## 🧪 Operation Modes
 
### **Test Mode (`--t`)**
- Collects feedback after each AI response
- Prompts for satisfaction rating (satisfied/neutral/unsatisfied)
- Optional reason for rating
- Used for improving AI model performance
- Saves feedback to dataset.json
- Shows detailed debug information
 
### **User Mode (`--u`)**
- Standard analysis mode
- No feedback collection
- Cleaner interface for regular use
- Focuses on analysis results
 
## 🛠️ Advanced Usage
 
### **Session Management**
```bash
# Check what's currently loaded
python pcap_ai.py --status
 
# Clear your session and start fresh  
python pcap_ai.py --clear
 
# Clear conversation history
python pcap_ai.py --clear-history
 
# Test mode with existing session
python pcap_ai.py --t
 
# User mode with existing session
python pcap_ai.py --u
```

### **Workflow Examples**

#### **🕵️ Protocol Specific Packet Analysis **
```bash
python pcap_ai.py
🤖 packetSense> How many write requests do you see in the trace?
🤖 packetSense> Can you summarize the response for packet 17?
🤖 packetSense> How many files were created in between 12:07:55 and 12:07:56 on 08/05/2025?
```

## 🏗️ Project Structure
```
pcapAI/
├── src/
│   ├── __init__.py
│   ├── pcap_analyzer.py        # Packet parsing and analysis
│   ├── ai_query_handler.py     # AI API integration and query handling
│   ├── packet_parser.py        # Core packet processing and JSON conversion
│   ├── protocols/
│   │   ├── __init__.py
│   │   ├── base.py             # Protocol base class
│   │   ├── nfs.py              # NFS protocol logic
│   │   ├── smb2.py             # SMB2 protocol logic
│   │   └── http.py             # HTTP protocol logic
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── filter.py           # Filtering logic (time, packet number, operation, etc.)
│   │   └── tool_calling_handler.py # Tool calling and chaining logic
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # Utility/helper functions
├── pcap_ai.py                  # Main entry point with session management
├── session_data.pkl            # Auto-generated session storage
├── requirements.txt            # Python dependencies
├── .gitignore                  # Excludes session and key files
└── README.md                   # This file
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
🤖 packetSense> Question 1  # ⚡ Instant response!
🤖 packetSense> Question 2  # ⚡ Instant response!
🤖 packetSense> Question 3  # ⚡ Instant response!

# Next day...
$ python pcap_ai.py
🤖 packetSense> New question  # ⚡ Everything restored instantly!
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
