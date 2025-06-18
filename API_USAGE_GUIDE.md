# 📞 Call Replay Analyzer - API Usage Guide

A detailed guide on how to use each endpoint of the Call Replay Analyzer API with step-by-step instructions and examples.

## 🚀 Quick Start

### Prerequisites
1. **Server Running**: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. **OpenAI API Key**: Set in `.env` file
3. **Test Data**: Use files in `examples/` directory

### Base URL
```
http://localhost:8000
```

---

## 📋 Endpoint Reference

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/analyze-call` | POST | Analyze single call | Raw transcript | Analysis result |
| `/analyze-batch` | POST | Analyze multiple calls | Array of transcripts | Batch results |
| `/prefilter-check` | POST | Test failure detection | Raw transcript | Prefilter result |
| `/generate-fixes` | POST | Get detailed fixes | Analysis result | Fix suggestions |
| `/generate-summary` | POST | Summarize analyses | Array of analyses | Summary report |
| `/stats` | GET | System statistics | None | System info |

---

## 🔍 1. Analyze Single Call (`/analyze-call`)

**Purpose**: Analyze one call transcript to detect issues and suggest fixes.

### Step-by-Step Instructions

#### Step 1: Prepare Your Data
Create a JSON file with this structure:
```json
{
  "call_id": "unique_call_identifier",
  "dialog": [
    {
      "speaker": "user",
      "text": "Customer message here"
    },
    {
      "speaker": "bot", 
      "text": "Bot response here"
    }
  ],
  "metadata": {
    "restaurant": "Restaurant Name",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

#### Step 2: Make the Request

**Using cURL:**
```bash
curl -X POST http://localhost:8000/analyze-call \
  -H "Content-Type: application/json" \
  -d @your_transcript.json
```

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/analyze-call" `
  -Method POST `
  -ContentType "application/json" `
  -Body (Get-Content "your_transcript.json" -Raw)
```

**Using Postman:**
1. Method: `POST`
2. URL: `http://localhost:8000/analyze-call`
3. Headers: `Content-Type: application/json`
4. Body: Raw JSON (paste your transcript)

#### Step 3: Understand the Response
```json
{
  "call_id": "call_12345",
  "status": "analyzed",  // or "skipped" or "error"
  "reason": null,
  "analysis": {
    "intent": "Customer wanted delivery info",
    "bot_response_summary": "Bot provided hours instead",
    "issue_detected": true,
    "issue_reason": "Intent misunderstanding",
    "suggested_fix": "Improve intent recognition",
    "confidence_score": 0.8
  },
  "error": null
}
```

### Example with Sample Data
```bash
# Use the provided sample file
curl -X POST http://localhost:8000/analyze-call \
  -H "Content-Type: application/json" \
  -d @examples/sample_call.json
```

---

## 📦 2. Analyze Multiple Calls (`/analyze-batch`)

**Purpose**: Process multiple call transcripts efficiently and get batch statistics.

### Step-by-Step Instructions

#### Step 1: Prepare Batch Data
Create a JSON file with multiple transcripts:
```json
{
  "transcripts": [
    {
      "call_id": "call_1",
      "dialog": [
        {"speaker": "user", "text": "Do you deliver to Bandra?"},
        {"speaker": "bot", "text": "We are open 11 to 10."}
      ]
    },
    {
      "call_id": "call_2",
      "dialog": [
        {"speaker": "user", "text": "I want to order pizza"},
        {"speaker": "bot", "text": "Great! What size?"}
      ]
    }
  ]
}
```

#### Step 2: Make the Request
```bash
curl -X POST http://localhost:8000/analyze-batch \
  -H "Content-Type: application/json" \
  -d @batch_transcripts.json
```

#### Step 3: Understand the Response
```json
{
  "results": [
    {
      "call_id": "call_1",
      "status": "analyzed",
      "analysis": { /* analysis object */ }
    },
    {
      "call_id": "call_2", 
      "status": "skipped",
      "reason": "No issues detected"
    }
  ],
  "summary": {
    "total_calls": 2,
    "analyzed": 1,
    "skipped": 1,
    "errors": 0,
    "issues_detected": 1,
    "issue_rate": 1.0,
    "average_confidence": 0.8,
    "success_rate": 1.0
  }
}
```

### Using the Batch Processor Script
```bash
# Process all JSON files in a directory
python examples/batch_processor.py examples/ --output results.json

# Process a single file
python examples/batch_processor.py examples/sample_call.json --output result.json
```

---

## 🔍 3. Prefilter Check (`/prefilter-check`)

**Purpose**: Test if a call would be flagged by the failure detection heuristics without doing full LLM analysis.

### Step-by-Step Instructions

#### Step 1: Use Same Data Format as `/analyze-call`
```json
{
  "call_id": "test_call",
  "dialog": [
    {"speaker": "user", "text": "Do you deliver to Bandra?"},
    {"speaker": "bot", "text": "We are open 11 to 10."}
  ]
}
```

#### Step 2: Make the Request
```bash
curl -X POST http://localhost:8000/prefilter-check \
  -H "Content-Type: application/json" \
  -d @test_transcript.json
```

#### Step 3: Understand the Response
```json
{
  "call_id": "test_call",
  "would_analyze": true,
  "confidence": 0.8,
  "reasons": [
    "User frustration detected: 'that's not what i asked'",
    "Bot confusion detected: 'i apologize'"
  ],
  "call_length": 4
}
```

---

## 🔧 4. Generate Detailed Fixes (`/generate-fixes`)

**Purpose**: Get detailed, actionable suggestions based on an existing analysis result.

### Step-by-Step Instructions

#### Step 1: Get Analysis Result First
Use `/analyze-call` to get an analysis result.

#### Step 2: Extract Analysis Object
From the response, extract the `analysis` object:
```json
{
  "intent": "Customer wanted delivery info",
  "bot_response_summary": "Bot provided hours instead",
  "issue_detected": true,
  "issue_reason": "Intent misunderstanding",
  "suggested_fix": "Improve intent recognition",
  "confidence_score": 0.8
}
```

#### Step 3: Send to Fixes Endpoint
```bash
curl -X POST http://localhost:8000/generate-fixes \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Customer wanted delivery info",
    "bot_response_summary": "Bot provided hours instead",
    "issue_detected": true,
    "issue_reason": "Intent misunderstanding",
    "suggested_fix": "Improve intent recognition",
    "confidence_score": 0.8
  }'
```

#### Step 4: Understand the Response
```json
{
  "prompt_improvements": [
    {
      "issue": "Bot doesn't recognize delivery queries",
      "current_prompt": "General restaurant assistant",
      "suggested_prompt": "Add delivery area checking logic",
      "rationale": "Will help bot understand delivery vs hours queries"
    }
  ],
  "logic_improvements": [
    {
      "issue": "No delivery area validation",
      "current_behavior": "Provides generic hours info",
      "suggested_behavior": "Check delivery areas first",
      "implementation": "Add delivery area database lookup"
    }
  ],
  "training_suggestions": [
    {
      "scenario": "Delivery inquiries",
      "examples": ["Do you deliver to X?", "Delivery available?"],
      "expected_outcome": "Direct yes/no response with area info"
    }
  ],
  "priority": "high",
  "estimated_impact": "Reduce customer frustration by 80%"
}
```

---

## 📊 5. Generate Summary (`/generate-summary`)

**Purpose**: Analyze multiple call analysis results to find patterns and common issues.

### ⚠️ Important: This endpoint expects ANALYSIS RESULTS, not raw transcripts!

### Step-by-Step Instructions

#### Step 1: Get Multiple Analysis Results
First, use `/analyze-batch` to get multiple analysis results.

#### Step 2: Extract Analysis Objects
From the batch response, extract the `analysis` objects from each result.

#### Step 3: Send Analysis Array to Summary
```bash
curl -X POST http://localhost:8000/generate-summary \
  -H "Content-Type: application/json" \
  -d '[
    {
      "intent": "Delivery inquiry",
      "bot_response_summary": "Provided hours instead",
      "issue_detected": true,
      "issue_reason": "Intent misunderstanding",
      "suggested_fix": "Add delivery logic",
      "confidence_score": 0.7
    },
    {
      "intent": "Pizza order",
      "bot_response_summary": "Handled order successfully", 
      "issue_detected": false,
      "issue_reason": "No issues",
      "suggested_fix": "None needed",
      "confidence_score": 0.9
    }
  ]'
```

#### Step 4: Understand the Response
```json
{
  "common_issues": [
    {
      "issue": "Intent recognition problems",
      "frequency": "50% of calls",
      "impact": "high"
    }
  ],
  "top_improvements": [
    {
      "improvement": "Add delivery area checking",
      "priority": "high",
      "expected_benefit": "Reduce customer frustration"
    }
  ],
  "overall_quality_score": 0.7,
  "trends": "Most issues relate to intent misunderstanding",
  "recommendations": [
    "Train bot on delivery queries",
    "Improve response relevance",
    "Add fallback responses"
  ]
}
```

---

## 📈 6. System Statistics (`/stats`)

**Purpose**: Get information about the system configuration and capabilities.

### Step-by-Step Instructions

#### Step 1: Make the Request
```bash
curl http://localhost:8000/stats
```

#### Step 2: Understand the Response
```json
{
  "model": "gpt-3.5-turbo",
  "temperature": 0.2,
  "max_retries": 3,
  "frustration_keywords_count": 16,
  "bot_confusion_patterns_count": 6,
  "short_response_threshold": 10
}
```

---

## 🔄 Complete Workflow Examples

### Example 1: Single Call Analysis
```bash
# 1. Analyze a call
curl -X POST http://localhost:8000/analyze-call \
  -H "Content-Type: application/json" \
  -d @examples/sample_call.json

# 2. Get detailed fixes (optional)
# Extract analysis object from step 1 and send to /generate-fixes
```

### Example 2: Batch Analysis + Summary
```bash
# 1. Analyze multiple calls
curl -X POST http://localhost:8000/analyze-batch \
  -H "Content-Type: application/json" \
  -d @batch_data.json

# 2. Extract analysis objects from step 1 response
# 3. Generate summary
curl -X POST http://localhost:8000/generate-summary \
  -H "Content-Type: application/json" \
  -d '[analysis_object_1, analysis_object_2]'
```

### Example 3: Testing Prefilter
```bash
# Test if call would be flagged
curl -X POST http://localhost:8000/prefilter-check \
  -H "Content-Type: application/json" \
  -d @test_call.json
```

---

## 🛠️ Troubleshooting

### Common Errors

#### 422 Unprocessable Content
- **Cause**: Wrong data format
- **Solution**: Check JSON structure matches expected schema

#### 500 Internal Server Error
- **Cause**: Missing OpenAI API key or API issues
- **Solution**: Check `.env` file and API key validity

#### "LLM call failed"
- **Cause**: OpenAI API issues or rate limits
- **Solution**: Check API key, billing, and retry

### Debug Tips

1. **Check server logs** for detailed error messages
2. **Validate JSON** using online JSON validators
3. **Test with sample data** first
4. **Use `/docs` endpoint** for interactive API testing

---

## 📚 Additional Resources

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Sample Data**: `examples/` directory
- **Batch Processor**: `examples/batch_processor.py`

---

## 🎯 Best Practices

1. **Always validate JSON** before sending
2. **Use batch processing** for multiple calls
3. **Save analysis results** for summary generation
4. **Monitor system stats** regularly
5. **Test with sample data** before production use 