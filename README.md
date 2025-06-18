# 📞 Call Replay Analyzer

A production-quality, AI-powered system for automatically detecting, analyzing, and fixing failed customer service calls. Built for seamless integration with Certus and other call analysis platforms.

## 🎯 Overview

The Call Replay Analyzer provides a complete automated workflow that:
1. **🔗 Receives failed calls** via webhooks from Certus (automatic)
2. **🧠 Detects issues** using intelligent heuristics and GPT-3.5 Turbo
3. **🔍 Analyzes problems** with detailed AI-powered insights
4. **🛠️ Suggests fixes** for prompt improvements and logic changes
5. **📊 Stores results** with comprehensive filtering and analytics
6. **📈 Provides insights** for continuous bot improvement

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Certus     │───▶│   Webhook API    │───▶│  Background     │───▶│   LLM Analyzer   │
│   (Failed    │    │   (/webhook)     │    │  Processing     │    │  (GPT-3.5 Turbo)│
│   Calls)     │    └──────────────────┘    └─────────────────┘    └─────────────────┘
└──────────────┘                                    │                        │
                                                    ▼                        ▼
                                            ┌─────────────────┐    ┌─────────────────┐
                                            │   Storage       │    │   Fix Generator  │
                                            │   (JSON + API)  │    │   (Detailed     │
                                            └─────────────────┘    │   Suggestions)   │
                                                    │               └─────────────────┘
                                                    ▼
                                            ┌─────────────────┐
                                            │   Analysis      │
                                            │   History API   │
                                            │   (Filtering)   │
                                            └─────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd Call_Analyser

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

# Or test the complete pipeline
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d @examples/batch_test.json
```

## 🔧 API Endpoints

### 🚀 **Core Analysis Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pipeline` | POST | **🚀 Complete automated workflow** - Analyze → Generate Fixes → Create Summary |
| `/analyze-call` | POST | Analyze a single call transcript |
| `/analyze-batch` | POST | Analyze multiple calls in batch |
| `/ingest-transcript` | POST | Ingest single transcript with metadata |

### 🔗 **Certus Integration**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | **🔗 Certus webhook** - Auto-ingest failed call transcripts |

### 📊 **Analysis History & Storage**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analysis-history` | GET | **📊 Get stored analysis history** with filtering |
| `/analysis-stats` | GET | **📈 Get analysis statistics** |
| `/analysis-backup` | POST | **💾 Create data backup** |
| `/analysis-history/{call_id}` | GET | **📋 Get call-specific history** |

### 🛠️ **Utility Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/prefilter-check` | POST | Test failure detection heuristics |
| `/generate-fixes` | POST | Generate detailed fix suggestions |
| `/generate-summary` | POST | Summarize multiple analyses |
| `/stats` | GET | Get system statistics |
| `/health` | GET | Health check |

## 🔗 **Certus Integration (Automatic)**

### Webhook Setup

Configure Certus to automatically send failed calls:

```bash
# Webhook URL
http://your-server:8000/webhook

# Test the webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d @examples/certus_webhook_test.json
```

### Expected Certus Payload

```json
{
  "call_id": "certus_call_12345",
  "dialog": [
    {"speaker": "user", "text": "Do you deliver to Bandra?"},
    {"speaker": "bot", "text": "We are open 11 to 10."}
  ],
  "metadata": {
    "certus_call_id": "certus_12345",
    "failure_reason": "intent_misunderstanding",
    "call_duration": 45,
    "customer_satisfaction": "low"
  }
}
```

## 📊 **Analysis History & Filtering**

### Get All Analysis History

```bash
# Get all stored analyses
curl http://localhost:8000/analysis-history

# Filter by date range
curl "http://localhost:8000/analysis-history?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z"

# Filter by status
curl "http://localhost:8000/analysis-history?status=analyzed&limit=10"

# Filter by call ID
curl "http://localhost:8000/analysis-history?call_id=call_12345"
```

### Get Statistics

```bash
# Get comprehensive statistics
curl http://localhost:8000/analysis-stats
```

## 🚀 **Complete Pipeline (Recommended)**

The `/pipeline` endpoint does everything automatically:

```bash
# Process batch with complete analysis
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d @examples/batch_test.json
```

**What it does automatically:**
1. ✅ Analyzes all transcripts
2. ✅ Generates detailed fixes for problematic calls
3. ✅ Creates comprehensive summary
4. ✅ Saves everything to files
5. ✅ Returns complete results with statistics

## 📊 **Sample Output**

### Analysis Result

```json
{
  "call_id": "call_12345",
  "status": "analyzed",
  "analysis": {
    "intent": "Delivery inquiry",
    "bot_response_summary": "Bot provided hours instead of delivery info",
    "issue_detected": true,
    "issue_reason": "Intent misunderstanding",
    "suggested_fix": "Add delivery area checking logic",
    "confidence_score": 0.85
  }
}
```

### Pipeline Result

```json
{
  "pipeline_id": "pipeline_20240115_143022",
  "input_count": 3,
  "analysis_results": [...],
  "fix_results": {
    "call_001": {
      "prompt_improvements": [...],
      "logic_improvements": [...],
      "priority": "high"
    }
  },
  "summary": {
    "common_issues": [...],
    "top_improvements": [...],
    "overall_quality_score": 0.8
  },
  "statistics": {
    "total_calls": 3,
    "analyzed": 1,
    "issues_detected": 1,
    "success_rate": 1.0
  }
}
```

## 🧠 **How It Works**

### 1. **Failure Detection (Prefilter)**
- **User frustration keywords**: "not helpful", "what?", "makes no sense"
- **Bot repetition**: Same responses multiple times
- **Conversation flow issues**: Very short responses, abrupt endings
- **Bot confusion patterns**: "I don't understand", "I'm sorry"

### 2. **LLM Analysis (GPT-3.5 Turbo)**
- **Intent recognition**: Did the bot understand the customer?
- **Response relevance**: Were answers helpful?
- **Conversation flow**: Was the interaction natural?
- **Problem resolution**: Was the customer's issue solved?

### 3. **Fix Generation**
- **Prompt improvements**: Better system prompts
- **Logic changes**: Improved conversation flow
- **Training suggestions**: Scenarios to train on

### 4. **Storage & Analytics**
- **Automatic storage**: All results saved with timestamps
- **Filtering**: Date range, status, call ID filtering
- **Statistics**: Comprehensive metrics and trends

## 📁 **Key Files**

### **Core System**
- `main.py` - FastAPI server with all endpoints
- `analyzer.py` - LLM analysis logic (GPT-3.5 Turbo)
- `prefilter.py` - Failure detection heuristics
- `prompt_builder.py` - LLM prompt generation
- `models.py` - Pydantic data models
- `storage.py` - Analysis history storage and filtering
- `pipeline.py` - Complete automated workflow

### **Documentation**
- `API_USAGE_GUIDE.md` - Complete API documentation with examples
- `CERTUS_INTEGRATION_GUIDE.md` - Detailed Certus setup guide

### **Examples & Testing**
- `examples/certus_webhook_test.json` - Sample webhook payload
- `examples/test_webhook.py` - Webhook testing script
- `examples/batch_test.json` - Sample batch data

## 🛠️ **Configuration**

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

## 📈 **Monitoring & Analytics**

### System Statistics

```bash
curl http://localhost:8000/stats
```

### Analysis History

```bash
# Get recent analyses
curl "http://localhost:8000/analysis-history?limit=10"

# Get statistics
curl http://localhost:8000/analysis-stats
```

### Webhook Monitoring

```bash
# Test webhook
python examples/test_webhook.py

# Check webhook results
curl "http://localhost:8000/analysis-history?status=analyzed&limit=5"
```

## 🚀 **Production Deployment**

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

## 🔒 **Security Considerations**

- **API Key Management**: Use environment variables, never commit keys
- **Input Validation**: All inputs validated via Pydantic models
- **Rate Limiting**: Implement rate limiting for production
- **CORS**: Configure CORS appropriately for your domain
- **HTTPS**: Use HTTPS in production for webhooks

## 📚 **Additional Documentation**

- **[API Usage Guide](API_USAGE_GUIDE.md)** - Complete API documentation with examples
- **[Certus Integration Guide](CERTUS_INTEGRATION_GUIDE.md)** - Detailed setup for Certus integration
- **Interactive API Docs**: `http://localhost:8000/docs` (when server is running)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/docs` when server is running
- Review the example files in the `examples/` directory
- Consult the detailed guides in the documentation files

---

**Built for production use with Certus and other call analysis platforms.**
**Features automatic webhook integration, comprehensive analysis history, and complete automated workflows.** 