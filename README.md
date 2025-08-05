# 🤖 AutoApply AI - Intelligent Job Application System

An AI-driven multi-agent system that automatically applies to jobs on LinkedIn and other platforms using sophisticated AI reasoning and form-filling capabilities.

## ✨ Features

- **🧠 AI-Powered Decision Making**: Uses multiple AI models (local + cloud) for intelligent job application
- **🌐 Beautiful Web Interface**: Modern, responsive dashboard with real-time updates
- **🤖 Multi-Agent Architecture**: Specialized agents for search, navigation, form filling, and monitoring
- **📊 Vector Database**: Semantic search and storage of user profile data
- **📧 Email Integration**: Automatic handling of verification emails
- **📈 Real-time Analytics**: Live statistics and progress tracking
- **⚙️ Configurable Settings**: Customizable delays, rate limits, and preferences

## 🏗️ Architecture

```
AutoApply AI/
├── 🎛️ Web Interface (web_interface/)
├── 🤖 AI Agents (agents/)
├── 🧠 LLM Interfaces (llm/)
├── 💾 Core Systems (core/)
├── 📊 Data Storage (data/, database/)
├── 🚀 Scripts (scripts/)
└── 📝 Logs (logs/)
```

### 🤖 AI Agents
- **JobSearchAgent**: Finds relevant jobs across platforms
- **NavigationAgent**: Handles web navigation and page interaction
- **FormFillingAgent**: Uses AI to intelligently fill application forms
- **EmailAgent**: Monitors and handles verification emails
- **OverlordAgent**: Monitors system health and handles recovery

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tlweave2/jobagent.git
cd jobagent

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys and settings
```

### 2. Configuration

```bash
# Add your profile data
cp data/user_profile.yaml.example data/user_profile.yaml
# Edit with your personal information

# Add your resume
cp your_resume.pdf resumes/

# Configure API keys in .env
```

### 3. Run the System

#### 🌐 Web Interface (Default & Recommended)
```bash
python start.py
```
The web interface will automatically open at http://localhost:8000

#### Alternative Options:
```bash
python run.py              # Launcher with options
python orchestrator.py     # Direct web interface
python scripts/start_web.py # Web interface from scripts
```

## 📁 Project Structure

```
jobagent/
├── 📱 web_interface/           # Web dashboard and server
│   ├── web_interface.html     # Main web interface
│   ├── web_server.py          # Backend web server
│   └── index.html             # Alternative interface
├── 🤖 agents/                 # AI agents
│   ├── job_search_agent.py    # Job discovery
│   ├── navigation_agent.py    # Web navigation
│   ├── form_filling_agent.py  # Form completion
│   ├── email_agent.py         # Email handling
│   └── overlord_agent.py      # System monitoring
├── 🧠 llm/                    # AI model interfaces
│   ├── local_llm.py           # Local models (Ollama)
│   └── cloud_llm.py           # Cloud models (Claude, GPT)
├── 💾 core/                   # Core systems
│   ├── vector_database.py     # ChromaDB integration
│   └── logger.py              # Application logging
├── 📊 data/                   # Configuration and profiles
│   ├── user_profile.yaml      # Your profile data
│   └── linkedin_search.yaml   # Search configurations
├── 🗄️ database/               # Vector database storage
├── 📝 logs/                   # Application logs
├── 🚀 scripts/                # Utility scripts
│   └── start_web.py           # Web interface launcher
├── 📄 resumes/                # Your resume files
├── 📋 coverletters/           # Cover letter templates
└── 🎛️ orchestrator.py         # Main system controller
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# AI API Keys
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993

# System Settings
DELAY_BETWEEN_JOBS=60
MAX_JOBS_PER_HOUR=10
ENABLE_EMAIL_MONITORING=true
```

### User Profile (data/user_profile.yaml)
```yaml
personal:
  name: "Your Name"
  email: "your.email@example.com"
  phone: "+1-555-123-4567"
  location: "City, State"

experience:
  - title: "Software Engineer"
    company: "Tech Corp"
    duration: "2020-2024"
    # ... more details

skills:
  - "Python"
  - "JavaScript"
  - "React"
  # ... more skills
```

## 🎮 Usage

### 🌐 Web Interface (Primary Method)
1. Run: `python start.py`
2. Web interface opens automatically at http://localhost:8000
3. Enter job search terms in the web dashboard
4. Configure settings as needed
5. Click "Start Applying" 
6. Monitor progress in real-time

### 💻 Command Line (Alternative)
1. Run: `python run.py` and select option 2
2. Enter search terms when prompted
3. Monitor progress in terminal

## 🛠️ Advanced Features

### AI Model Configuration
- **Local LLM**: Uses Ollama for fast, private processing
- **Cloud LLM**: Uses Claude/GPT for complex reasoning
- **Fallback System**: Automatically switches between models

### Multi-Platform Support
- LinkedIn (primary)
- Indeed (planned)
- Glassdoor (planned)
- Company career pages (planned)

### Smart Form Filling
- AI reads and understands form fields
- Intelligently maps profile data to forms
- Handles complex screening questions
- Adapts to different form layouts

## 📊 Monitoring & Analytics

- **Real-time Dashboard**: Live job queue and application status
- **Success Metrics**: Application rates, success percentages
- **Detailed Logs**: Comprehensive activity logging
- **Error Tracking**: Automatic error detection and reporting

## 🔧 Troubleshooting

### Common Issues

1. **Installation Problems**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

2. **Browser Issues**
   ```bash
   playwright install chromium
   ```

3. **API Key Issues**
   - Check .env file configuration
   - Verify API key validity
   - Check rate limits

### Logs
Check `logs/applications.yaml` for detailed application logs and error information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Please respect website terms of service and rate limits. Use responsibly and in compliance with platform policies.

## 🆘 Support

- 📧 Email: support@autoapply-ai.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Made with ❤️ and 🤖 AI**
