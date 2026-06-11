# Inbox-IQ: AI-Powered Email Triage System

An intelligent email management system that uses AI to automatically categorize, prioritize, and respond to emails with minimal human intervention.

## 📋 Project Overview

Inbox-IQ is a machine learning-based email triage system designed to help users efficiently manage their email inbox by:
- **Automatic Categorization**: Classify emails into predefined categories
- **Priority Detection**: Identify urgent and important emails
- **Smart Responses**: Generate contextual replies using AI
- **Gmail Integration**: Seamless integration with Gmail API
- **Personalized Emails**: Send personalized follow-up emails based on email content

## 🚀 Features

- 📧 **Gmail Integration**: Direct Gmail API connection with OAuth authentication
- 🤖 **AI-Powered Analysis**: Uses large language models for email understanding
- 🏷️ **Intelligent Categorization**: Automatically classify emails
- ⚡ **Priority Scoring**: Rate emails by urgency
- 💬 **Automated Responses**: Generate intelligent email replies
- 🌐 **Web Interface**: Flask-based web application for easy access
- 📊 **Performance Grading**: Evaluate system accuracy and performance

## 📁 Project Structure

```
metaHackthon/
├── files/
│   ├── agent_loop.py              # Main agent orchestration logic
│   ├── gmail_auth.py              # Gmail OAuth authentication
│   ├── inference.py               # Core inference engine
│   ├── inference_gmail.py         # Gmail-specific inference
│   ├── inference_gmail_with_send.py # Inference with email sending
│   ├── send_personalized_email.py # Email composition and sending
│   ├── grader.py                  # Performance evaluation
│   ├── web_app.py                 # Flask web interface
│   ├── environment.py             # Environment configuration
│   ├── tasks.py                   # Task definitions
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container configuration
│   └── README.md                  # Detailed file documentation
├── openenv.yaml                   # OpenAI/LLM configuration
└── credentials/                   # (Not included - add your own)
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Gmail account with API access
- OpenAI API key (or alternative LLM)
- Git

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/Susmitha967/Inbox-IQ-.git
cd Inbox-IQ-/AI-EMAIL-TRIAGE-SYSTEM
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
cd metaHackthon/files
pip install -r requirements.txt
```

4. **Configure Environment**
- Create `.env` file with your credentials:
  ```
  GMAIL_EMAIL=your_email@gmail.com
  OPENAI_API_KEY=your_api_key
  LLM_MODEL=gpt-4
  ```
- Set up `openenv.yaml` with LLM configuration

5. **Gmail API Setup**
- Download credentials from Google Cloud Console
- Place `credentials.json` in the project directory
- Run initial authentication to generate `token.pickle`

## 📝 Usage

### Running the Main Agent
```bash
python agent_loop.py
```

### Running Inference Only
```bash
python inference_gmail.py
```

### Sending Personalized Emails
```bash
python send_personalized_email.py
```

### Starting Web Interface
```bash
python web_app.py
```

### Grading Performance
```bash
python grader.py
```

## 🐳 Docker Deployment

Build and run using Docker:
```bash
docker build -t inbox-iq .
docker run -v $(pwd)/credentials:/app/credentials inbox-iq
```

## 📊 Configuration

Edit `openenv.yaml` to configure:
- LLM model selection
- Temperature and parameters
- Prompt templates
- Email categorization rules

## 🔐 Security Notes

⚠️ **IMPORTANT**: 
- Never commit `credentials.json` or `token.pickle`
- Never commit `.env` files with API keys
- Add these to `.gitignore`
- Use environment variables for sensitive data

## 🧪 Testing & Evaluation

- Run `grader.py` to evaluate system performance
- Debug tools available in `debug_*.py` files
- Check inference accuracy against known test cases

## 📈 Performance Metrics

System generates:
- `results.json` - Raw inference results
- `results_gmail.json` - Gmail-specific results
- `agent_log.json` - Agent execution logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Push to your branch
5. Open a Pull Request

## 📄 License

This project is provided as-is for educational and commercial use.

## 👨‍💻 Author

**Susmitha** - [GitHub Profile](https://github.com/Susmitha967)

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced sentiment analysis
- [ ] Custom training models
- [ ] Mobile app integration
- [ ] Real-time email streaming
- [ ] Advanced analytics dashboard

## 📞 Support

For issues, questions, or suggestions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Contact the project maintainer

## 🙏 Acknowledgments

Built with:
- OpenAI GPT models
- Google Gmail API
- Flask
- Python ecosystem

---

**Last Updated**: June 2026  
**Status**: Active Development
