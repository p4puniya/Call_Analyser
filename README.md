# 📞 Call Replay Analyzer

A production-quality, AI-powered system for automatically detecting and analyzing failed customer service calls. Built for integration with Certus and other call analysis platforms.

## 🎯 Overview

The Call Replay Analyzer automatically:
1. **Detects failing calls** using intelligent heuristics
2. **Analyzes issues** with GPT-powered LLM analysis
3. **Suggests fixes** for prompt improvements and logic changes
4. **Provides insights** for continuous bot improvement

## 🏗️ Architecture

```
┌──────────────┐       ┌──────────────────┐        ┌─────────────────┐
│ Transcript   │─────▶│ Failure Detector  │──────▶│ LLM Analyzer     │
│ (from Certus)│       └──────────────────┘        └─────────────────┘
│              │                                    │ Suggests fixes  │
└──────────────┘                                    ▼
                                              ┌───────────────┐
                                              │ API + Storage │
                                              └───────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd call_replay_analyzer

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Configure API Key

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
LOG_LEVEL=INFO
```

### 3. Start the Server

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the System

```bash
# Test with sample data
curl -X POST http://localhost:8000/analyze-call \
  -H "Content-Type: application/json" \
  -d @examples/sample_call.json
```

## 📁 Project Structure

```
call_replay_analyzer/
├── main.py                 # FastAPI API server
├── analyzer.py             # LLM analysis logic
├── prefilter.py            # Failure detection heuristics
├── prompt_builder.py       # LLM prompt generation
├── models.py               # Pydantic data models
├── examples/
│   ├── sample_call.json    # Failed call example
│   ├── successful_call.json # Successful call example
│   └── batch_processor.py  # Batch processing script
├── requirements.txt        # Python dependencies
├── env.example            # Environment template
└── README.md              # This file
```

## 🔧 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze-call` | POST | Analyze a single call transcript |
| `/analyze-batch` | POST | Analyze multiple calls in batch |
| `/prefilter-check` | POST | Check if call would be flagged |
| `/generate-fixes` | POST | Generate detailed fix suggestions |
| `/generate-summary` | POST | Summarize multiple analyses |
| `/stats` | GET | Get system statistics |

### Example Usage

#### Analyze Single Call

```bash
curl -X POST http://localhost:8000/analyze-call \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_123",
    "dialog": [
      {"speaker": "user", "text": "Do you deliver to Bandra?"},
      {"speaker": "bot", "text": "We are open 11 to 10."},
      {"speaker": "user", "text": "That\'s not what I asked."}
    ]
  }'
```

#### Batch Processing

```bash
# Using the batch processor script
python examples/batch_processor.py examples/ --output results.json

# Or via API directly
curl -X POST http://localhost:8000/analyze-batch \
  -H "Content-Type: application/json" \
  -d @batch_request.json
```

## 🧠 How It Works

### 1. Failure Detection (Prefilter)

The system uses intelligent heuristics to detect potentially failed calls:

- **User frustration keywords**: "not helpful", "what?", "makes no sense"
- **Bot repetition**: Same responses multiple times
- **Conversation flow issues**: Very short responses, abrupt endings
- **Bot confusion patterns**: "I don't understand", "I'm sorry"

### 2. LLM Analysis

For calls flagged by the prefilter, GPT-4 analyzes:

- **Intent recognition**: Did the bot understand the customer?
- **Response relevance**: Were answers helpful?
- **Conversation flow**: Was the interaction natural?
- **Problem resolution**: Was the customer's issue solved?

### 3. Fix Generation

The system suggests specific improvements:

- **Prompt improvements**: Better system prompts
- **Logic changes**: Improved conversation flow
- **Training suggestions**: Scenarios to train on

## 📊 Sample Output

```json
{
  "call_id": "call_12345",
  "status": "analyzed",
  "analysis": {
    "intent": "Customer wanted to know delivery availability",
    "bot_response_summary": "Bot provided hours instead of delivery info",
    "issue_detected": true,
    "issue_reason": "Bot misunderstood delivery question as hours question",
    "suggested_fix": "Add delivery area checking logic to prompt",
    "confidence_score": 0.85,
    "severity": "high",
    "categories": ["intent_misunderstanding", "irrelevant_response"],
    "key_moments": [
      {
        "turn": "2",
        "speaker": "bot",
        "issue": "Provided hours instead of delivery info"
      }
    ]
  }
}
```

## 🔌 Certus Integration

### Webhook Integration

Configure Certus to POST call transcripts to your analyzer:

```python
# Certus webhook configuration
WEBHOOK_URL = "https://your-analyzer.com/analyze-call"
TRIGGER_CONDITIONS = [
    "call_completed",
    "low_satisfaction_score",
    "abnormal_duration"
]
```

### Batch Processing

For high-volume scenarios, use batch processing:

```python
# Process daily call logs
python examples/batch_processor.py /path/to/calls/ --output daily_analysis.json
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `LOG_LEVEL` | Logging level | INFO |

### Customization

#### Adding New Failure Patterns

Edit `prefilter.py`:

```python
# Add new frustration keywords
self.frustration_keywords.extend([
    "your_new_keyword",
    "another_pattern"
])
```

#### Customizing Prompts

Edit `prompt_builder.py`:

```python
# Modify system prompt for your domain
self.system_prompt = "You are an expert analyzing [YOUR_DOMAIN] calls..."
```

## 📈 Monitoring & Analytics

### System Statistics

```bash
curl http://localhost:8000/stats
```

Returns:
```json
{
  "model": "gpt-4o",
  "temperature": 0.2,
  "max_retries": 3,
  "frustration_keywords_count": 16,
  "bot_confusion_patterns_count": 6,
  "short_response_threshold": 10
}
```

### Analysis Metrics

The system tracks:
- **Issue detection rate**: Percentage of calls with issues
- **Confidence scores**: Analysis reliability
- **Common problems**: Most frequent issues
- **Success rates**: Processing success metrics

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

```bash
# Production environment
export OPENAI_API_KEY="sk-..."
export LOG_LEVEL="WARNING"
export WORKERS=4

# Start with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers $WORKERS
```

## 🔒 Security Considerations

- **API Key Management**: Use environment variables, never commit keys
- **Input Validation**: All inputs validated via Pydantic models
- **Rate Limiting**: Implement rate limiting for production
- **CORS**: Configure CORS appropriately for your domain

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/docs` when server is running
- Review the example files in the `examples/` directory

---

**Built for production use with Certus and other call analysis platforms.** 