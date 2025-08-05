# LinkedIn Job Auto-Applier

An AI-powered automation system for applying to LinkedIn jobs using Easy Apply. This system combines computer vision, natural language processing, and browser automation to intelligently fill out job application forms.

## 🌟 Features

- **GUI Frontend**: User-friendly Tkinter interface for managing job searches
- **Dual AI Models**: 
  - Local LLM (Ollama qwen2.5vl:7b) with vision capabilities
  - Cloud LLM (Anthropic Claude) as backup/alternative
- **Smart Form Detection**: Analyzes page screenshots and DOM structure
- **Profile Management**: YAML-based user profile configuration
- **LinkedIn Integration**: Specialized handling of LinkedIn's Easy Apply system
- **Real-time Logging**: Live status updates and detailed operation logs
- **Batch Processing**: Apply to multiple jobs automatically with search filters

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GUI Frontend  │────│   Controller     │────│  Browser Driver │
│ (Tkinter App)   │    │ (Job Automation) │    │  (Playwright)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐              │
         │              │                 │              │
         └──────────────▼─────────────────▼──────────────┘
                   ┌─────────────┐  ┌─────────────┐
                   │ Local LLM   │  │ Cloud LLM   │
                   │ (Ollama)    │  │ (Claude)    │
                   └─────────────┘  └─────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.12+
- Ollama server with qwen2.5vl:7b model
- Anthropic API key (optional, for cloud LLM)

### 2. Installation

```bash
# Clone and setup
cd jobagent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 3. Configuration

#### User Profile (`data/user_profile.yaml`)
```yaml
full_name: "Your Name"
email: "your.email@example.com"
phone: "+1-555-123-4567"
location: "Your City, State"
visa_status: "Authorized to work in the U.S."
resume_path: "./resumes/your_resume.pdf"
cover_letter_path: "./coverletters/cover_letter.pdf"
```

#### Environment Variables (`.env`)
```bash
# Local LLM Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5vl:7b

# Cloud LLM Settings (optional)
ANTHROPIC_API_KEY=your_claude_api_key_here

# Browser Settings
HEADLESS_MODE=false
MIN_DELAY_BETWEEN_APPS=3
```

### 4. Start Ollama Server

```bash
# Start Ollama server
ollama serve

# Pull the vision model (if not already installed)
ollama pull qwen2.5vl:7b
```

### 5. Login to LinkedIn

**Important**: You must be logged into LinkedIn for the automation to work.

```bash
# First-time setup: Login helper
python linkedin_login.py
```

This will:
- Open a browser window
- Navigate to LinkedIn login
- Save your session for future automation
- **Note**: You only need to do this once

### 6. Run the Application

#### GUI Mode (Recommended)
```bash
python linkedin_job_app.py
```

#### Command Line Mode
```bash
# Apply to a specific job
python -c "from agent.controller import apply_to_job; apply_to_job('https://linkedin.com/jobs/view/XXXXXX')"
```

#### Test System
```bash
python test_system.py
```

## 🎯 Usage Guide

### GUI Application

1. **Configure Profile**: 
   - Set your profile path (default: `data/user_profile.yaml`)
   - Choose AI model (Local Ollama or Cloud Claude)

2. **Set Job Search Parameters**:
   - Keywords: "Software Engineer", "Python Developer", etc.
   - Location: "San Francisco, CA", "Remote", etc.
   - Experience Level: Entry, Mid, Senior
   - Maximum applications to send

3. **Start Automation**:
   - Click "Start Job Search" 
   - Monitor real-time logs
   - Use "Stop" to halt the process

### LinkedIn Search Filters

The system supports LinkedIn's search parameters:
- **Keywords**: Job title, skills, company names
- **Location**: City, state, or "Remote"
- **Experience Level**: Entry level, Associate, Mid-Senior, Director, Executive
- **Easy Apply Only**: Filter for jobs with Easy Apply enabled
- **Date Posted**: Last 24 hours, Past week, Past month

## 🧠 AI Models

### Local LLM (Ollama qwen2.5vl:7b)
- **Vision Capabilities**: Analyzes page screenshots
- **Fast Processing**: Local inference, no API costs
- **Privacy**: All data stays local
- **Fallback**: Graceful text-only mode if vision fails

### Cloud LLM (Anthropic Claude)
- **High Accuracy**: Advanced reasoning capabilities
- **Vision Support**: Multi-modal analysis
- **Recovery Mode**: Handles complex scenarios
- **API Costs**: Pay per usage

## 📁 Project Structure

```
jobagent/
├── agent/                  # Core automation logic
│   ├── controller.py       # Main job application orchestrator
│   ├── memory_manager.py   # Session state management
│   ├── profile_agent.py    # Profile-specific logic
│   └── recovery_agent.py   # Error recovery system
├── browser/                # Browser automation
│   ├── playwright_driver.py # Main browser interface
│   └── dom_utils.py        # DOM manipulation utilities
├── models/                 # AI model interfaces
│   ├── local_llm.py        # Ollama integration
│   └── cloud_llm.py        # Claude/GPT integration
├── search/                 # LinkedIn search logic
│   ├── job_card_extractor.py # Job listing parser
│   └── linkedin_url_builder.py # Search URL generation
├── data/                   # Configuration and profiles
│   ├── user_profile.yaml   # User information
│   └── linkedin_search.yaml # Search templates
├── resumes/                # Resume files
├── coverletters/           # Cover letter files
├── scripts/                # Utility and test scripts
├── linkedin_job_app.py     # Main GUI application
├── test_system.py          # System verification
└── requirements.txt        # Python dependencies
```

## 🔧 Advanced Configuration

### Browser Settings
```python
# Headless mode (no visible browser)
HEADLESS_MODE=true

# Custom delays (seconds)
MIN_DELAY_BETWEEN_APPS=5
MAX_DELAY_BETWEEN_APPS=10

# Screenshot settings
SCREENSHOT_COMPRESSION=true
```

### AI Model Settings
```python
# Ollama configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5vl:7b
OLLAMA_TIMEOUT=60

# Claude configuration  
ANTHROPIC_API_KEY=your_key
CLAUDE_MODEL=claude-3-haiku-20240307
```

### LinkedIn Automation
```python
# Application limits
MAX_APPLICATIONS_PER_SESSION=50
MAX_STEPS_PER_APPLICATION=10

# Error handling
MAX_RETRIES=3
STALL_DETECTION_THRESHOLD=3
```

## 🛠️ Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/version
   
   # Start Ollama
   ollama serve
   ```

2. **Playwright Browser Issues**
   ```bash
   # Reinstall browsers
   playwright install
   
   # Check browser availability
   playwright --version
   ```

3. **LinkedIn Login Required**
   - The system expects you to be logged into LinkedIn
   - Use non-headless mode to manually log in
   - Consider using LinkedIn session cookies

4. **API Rate Limits**
   - Anthropic Claude has usage limits
   - Implement delays between requests
   - Monitor API usage in Anthropic console

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Privacy & Ethics

### Data Handling
- All profile data stored locally in YAML files
- Screenshots processed locally (unless using cloud LLM)
- No persistent storage of LinkedIn data
- Browser sessions isolated and cleaned up

### Ethical Use
- **Respect LinkedIn's Terms of Service**
- Use reasonable delays between applications
- Don't spam employers with irrelevant applications
- Ensure applications are high-quality and targeted

### Rate Limiting
- Built-in delays prevent overwhelming LinkedIn's servers
- Configurable application limits per session
- Automatic stall detection and recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black . && isort .

# Type checking
mypy jobagent/
```

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Ensuring applications are accurate and relevant
- Respecting rate limits and automated access policies
- Using the tool ethically and responsibly

The authors are not responsible for any consequences of using this automation tool.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM infrastructure
- [Playwright](https://playwright.dev/) for browser automation
- [Anthropic](https://anthropic.com/) for Claude API
- [LinkedIn](https://linkedin.com/) for the Easy Apply platform

---

**Built with ❤️ for job seekers everywhere** 🚀