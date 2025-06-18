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
| `/pipeline` | POST | **🚀 Complete automated workflow** | Array of transcripts | Full pipeline results |
| `/ingest-transcript` | POST | Ingest single transcript | Transcript + metadata | Ingestion status |
| `/prefilter-check` | POST | Test failure detection | Raw transcript | Prefilter result |
| `/generate-fixes` | POST | Get detailed fixes | Analysis result | Fix suggestions |
| `/generate-summary` | POST | Summarize analyses | Array of analyses | Summary report |
| `/analysis-history` | GET | **📊 Get stored analysis history** | Query parameters | Filtered results |
| `/analysis-stats` | GET | **📈 Get analysis statistics** | None | Statistics report |
| `/analysis-backup` | POST | **💾 Create data backup** | Optional path | Backup status |
| `/analysis-history/{call_id}` | GET | **📋 Get call-specific history** | Call ID | Call history |
| `/stats` | GET | System statistics | None | System info |

---

## 🚀 **NEW: Complete Pipeline (`/pipeline`)**

**Purpose**: **One endpoint that does everything automatically!** This is the main endpoint you'll want to use for processing batches of calls.

### What It Does Automatically:
1. ✅ **Analyzes all transcripts** in the batch
2. ✅ **Generates detailed fixes** for problematic calls
3. ✅ **Creates comprehensive summary** of all results
4. ✅ **Saves everything to files** for later review
5. ✅ **Returns complete results** with statistics

### Step-by-Step Instructions

#### Step 1: Prepare Your Batch Data
Use the same format as `/analyze-batch`:
```json
{
  "transcripts": [
    {
      "call_id": "call_001",
      "dialog": [
        {"speaker": "user", "text": "Do you deliver to Bandra?"},
        {"speaker": "bot", "text": "We are open 11 to 10."}
      ],
      "metadata": {
        "restaurant": "Sample Restaurant",
        "timestamp": "2024-01-15T14:30:00Z",
        "status": "failed"
      }
    },
    {
      "call_id": "call_002",
      "dialog": [
        {"speaker": "user", "text": "I want to order pizza"},
        {"speaker": "bot", "text": "Great! What size?"}
      ],
      "metadata": {
        "restaurant": "Sample Restaurant", 
        "timestamp": "2024-01-15T15:45:00Z",
        "status": "success"
      }
    }
  ]
}
```

#### Step 2: Make the Request
```bash
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d @examples/batch_test.json
```

#### Step 3: Understand the Response
```json
{
  "pipeline_id": "pipeline_20240115_143022",
  "timestamp": "2024-01-15T14:30:22.123456",
  "input_count": 3,
  "analysis_results": [
    {
      "call_id": "call_001",
      "status": "analyzed",
      "analysis": {
        "intent": "Delivery inquiry",
        "bot_response_summary": "Bot provided hours instead",
        "issue_detected": true,
        "issue_reason": "Intent misunderstanding",
        "suggested_fix": "Improve intent recognition",
        "confidence_score": 0.8
      }
    }
  ],
  "fix_results": {
    "call_001": {
      "prompt_improvements": [
        {
          "issue": "Bot doesn't recognize delivery queries",
          "suggested_prompt": "Add delivery area checking logic",
          "rationale": "Will help bot understand delivery vs hours queries"
        }
      ],
      "logic_improvements": [
        {
          "issue": "No delivery area validation",
          "suggested_behavior": "Check delivery areas first",
          "implementation": "Add delivery area database lookup"
        }
      ],
      "priority": "high",
      "estimated_impact": "Reduce customer frustration by 80%"
    }
  },
  "summary": {
    "common_issues": [
      {
        "issue": "Intent recognition problems",
        "frequency": "33% of calls",
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
    "overall_quality_score": 0.8,
    "trends": "Most issues relate to intent misunderstanding",
    "recommendations": [
      "Train bot on delivery queries",
      "Improve response relevance"
    ]
  },
  "statistics": {
    "total_calls": 3,
    "analyzed": 1,
    "skipped": 2,
    "errors": 0,
    "issues_detected": 1,
    "issue_rate": 1.0,
    "average_confidence": 0.8,
    "success_rate": 1.0,
    "processing_efficiency": 1.0
  }
}
```

### Files Created
The pipeline automatically saves:
- `data/pipeline_[timestamp].json` - Complete pipeline results
- `data/transcript_[call_id].json` - Individual transcripts
- `data/analysis_[call_id].json` - Individual analysis results

---

## 📥 **NEW: Ingest Transcript (`/ingest-transcript`)**

**Purpose**: Receive individual transcripts (e.g., from Certus webhooks) and optionally trigger immediate analysis.

### Step-by-Step Instructions

#### Step 1: Prepare Transcript with Metadata
```json
{
  "call_id": "call_12345",
  "dialog": [
    {"speaker": "user", "text": "Do you deliver to Bandra?"},
    {"speaker": "bot", "text": "We are open 11 to 10."}
  ],
  "metadata": {
    "restaurant": "Sample Restaurant",
    "timestamp": "2024-01-15T14:30:00Z",
    "status": "failed"  // This triggers immediate analysis
  }
}
```

#### Step 2: Make the Request
```bash
curl -X POST http://localhost:8000/ingest-transcript \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_12345",
    "dialog": [
      {"speaker": "user", "text": "Do you deliver to Bandra?"},
      {"speaker": "bot", "text": "We are open 11 to 10."}
    ],
    "metadata": {
      "status": "failed"
    }
  }'
```

#### Step 3: Understand the Response
```json
{
  "status": "received_and_analyzing",  // or "received" if not failed
  "call_id": "call_12345",
  "message": "Transcript received and analysis started"
}
```

### Use Cases
- **Certus webhook integration**: Send failed calls for immediate analysis
- **Real-time processing**: Process calls as they come in
- **Batch collection**: Store calls for later batch processing

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

## 📊 **NEW: Analysis History (`/analysis-history`)**

**Purpose**: Retrieve stored analysis results with powerful filtering capabilities. All analysis results are automatically saved and can be queried with various filters.

### What Gets Stored Automatically
Every time you use `/analyze-call`, `/analyze-batch`, or `/pipeline`, the results are automatically saved to persistent storage with timestamps.

### Step-by-Step Instructions

#### Step 1: Get All Analysis History
```bash
curl http://localhost:8000/analysis-history
```

#### Step 2: Filter by Date Range
```bash
# Get analyses from January 2024
curl "http://localhost:8000/analysis-history?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z"

# Get analyses from last 7 days
curl "http://localhost:8000/analysis-history?start_date=2024-01-08T00:00:00Z"
```

#### Step 3: Filter by Status
```bash
# Get only analyzed calls
curl "http://localhost:8000/analysis-history?status=analyzed"

# Get only skipped calls
curl "http://localhost:8000/analysis-history?status=skipped"

# Get only error calls
curl "http://localhost:8000/analysis-history?status=error"
```

#### Step 4: Filter by Call ID
```bash
# Get all analyses for a specific call
curl "http://localhost:8000/analysis-history?call_id=call_12345"
```

#### Step 5: Limit Results
```bash
# Get only the 10 most recent analyses
curl "http://localhost:8000/analysis-history?limit=10"

# Combine filters
curl "http://localhost:8000/analysis-history?status=analyzed&limit=5&start_date=2024-01-01T00:00:00Z"
```

#### Step 6: Understand the Response
```json
{
  "total_results": 15,
  "filters_applied": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": null,
    "call_id": null,
    "status": "analyzed",
    "limit": 5
  },
  "results": [
    {
      "call_id": "call_12345",
      "status": "analyzed",
      "analysis": {
        "intent": "Delivery inquiry",
        "bot_response_summary": "Bot provided hours instead",
        "issue_detected": true,
        "issue_reason": "Intent misunderstanding",
        "suggested_fix": "Add delivery logic",
        "confidence_score": 0.8
      },
      "timestamp": "2024-01-15T14:30:22.123456"
    }
  ]
}
```

### Available Query Parameters
- `start_date`: ISO format date (e.g., "2024-01-01T00:00:00Z")
- `end_date`: ISO format date (e.g., "2024-12-31T23:59:59Z")
- `call_id`: Specific call ID to filter by
- `status`: "analyzed", "skipped", or "error"
- `limit`: Maximum number of results (1-1000)

---

## 📈 **NEW: Analysis Statistics (`/analysis-stats`)**

**Purpose**: Get comprehensive statistics about all stored analysis data.

### Step-by-Step Instructions

#### Step 1: Get Statistics
```bash
curl http://localhost:8000/analysis-stats
```

#### Step 2: Understand the Response
```json
{
  "total_analyses": 150,
  "date_range": {
    "earliest": "2024-01-01T10:00:00Z",
    "latest": "2024-01-15T18:30:00Z",
    "span_days": 14
  },
  "status_breakdown": {
    "analyzed": 45,
    "skipped": 95,
    "error": 10
  },
  "unique_calls": 150,
  "call_ids": [
    "call_12345",
    "call_12346",
    "call_12347"
  ]
}
```

### What the Statistics Show
- **Total analyses**: How many calls have been processed
- **Date range**: When the first and last analyses were performed
- **Status breakdown**: How many calls were analyzed vs skipped vs errored
- **Unique calls**: How many different call IDs were processed
- **Call IDs**: Preview of the first 10 call IDs

---

## 💾 **NEW: Analysis Backup (`/analysis-backup`)**

**Purpose**: Create a backup of all analysis data before clearing or for data migration.

### Step-by-Step Instructions

#### Step 1: Create Automatic Backup
```bash
curl -X POST http://localhost:8000/analysis-backup
```

#### Step 2: Create Custom Backup
```bash
curl -X POST http://localhost:8000/analysis-backup \
  -H "Content-Type: application/json" \
  -d '"data/my_custom_backup.json"'
```

#### Step 3: Understand the Response
```json
{
  "message": "Analysis backup created successfully",
  "status": "success"
}
```

### Backup File Location
- **Automatic**: `data/analyzed_calls_backup_YYYYMMDD_HHMMSS.json`
- **Custom**: Path you specify

---

## 📋 **NEW: Call-Specific History (`/analysis-history/{call_id}`)**

**Purpose**: Get all analysis records for a specific call ID.

### Step-by-Step Instructions

#### Step 1: Get Call History
```bash
curl http://localhost:8000/analysis-history/call_12345
```

#### Step 2: Understand the Response
```json
{
  "call_id": "call_12345",
  "total_records": 3,
  "results": [
    {
      "call_id": "call_12345",
      "status": "analyzed",
      "analysis": {
        "intent": "Delivery inquiry",
        "bot_response_summary": "Bot provided hours instead",
        "issue_detected": true,
        "issue_reason": "Intent misunderstanding",
        "suggested_fix": "Add delivery logic",
        "confidence_score": 0.8
      },
      "timestamp": "2024-01-15T14:30:22.123456"
    }
  ]
}
```

### Use Cases
- Track how a specific call was processed over time
- Debug issues with specific calls
- Monitor re-analysis of the same call

---

## 🗑️ **NEW: Clear Analysis History (`DELETE /analysis-history`)**

**⚠️ WARNING: This permanently deletes all stored analysis data!**

### Step-by-Step Instructions

#### Step 1: Create Backup First (Recommended)
```bash
curl -X POST http://localhost:8000/analysis-backup
```

#### Step 2: Clear All Data
```bash
curl -X DELETE http://localhost:8000/analysis-history
```

#### Step 3: Understand the Response
```json
{
  "message": "Analysis history cleared successfully",
  "status": "success"
}
```

### When to Use
- **Testing**: Clear data between test runs
- **Data migration**: Clear old data after migration
- **Privacy**: Remove sensitive data
- **Storage cleanup**: Free up disk space

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

### Example 1: **🚀 RECOMMENDED - Complete Pipeline**
```bash
# One endpoint does everything automatically!
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d @examples/batch_test.json
```

### Example 2: **📥 Real-time Ingestion**
```bash
# Ingest a failed call for immediate analysis
curl -X POST http://localhost:8000/ingest-transcript \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_12345",
    "dialog": [
      {"speaker": "user", "text": "Do you deliver to Bandra?"},
      {"speaker": "bot", "text": "We are open 11 to 10."}
    ],
    "metadata": {"status": "failed"}
  }'
```

### Example 3: **Manual Step-by-Step**
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

### Example 4: **Testing Prefilter**
```bash
# Test if call would be flagged
curl -X POST http://localhost:8000/prefilter-check \
  -H "Content-Type: application/json" \
  -d @test_call.json
```

### Example 5: **📊 Analysis History Workflow**
```bash
# 1. Get all analysis history
curl http://localhost:8000/analysis-history

# 2. Get statistics about stored data
curl http://localhost:8000/analysis-stats

# 3. Filter by date range (last 7 days)
curl "http://localhost:8000/analysis-history?start_date=2024-01-08T00:00:00Z"

# 4. Get only problematic calls
curl "http://localhost:8000/analysis-history?status=analyzed&limit=10"

# 5. Get history for specific call
curl http://localhost:8000/analysis-history/call_12345

# 6. Create backup before clearing
curl -X POST http://localhost:8000/analysis-backup
```

### Example 6: **📈 Data Analysis Workflow**
```bash
# 1. Process calls with pipeline
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d @batch_data.json

# 2. Get analysis statistics
curl http://localhost:8000/analysis-stats

# 3. Filter recent problematic calls
curl "http://localhost:8000/analysis-history?status=analyzed&start_date=2024-01-01T00:00:00Z"

# 4. Generate summary from stored analyses
# (Extract analysis objects from step 3 and use /generate-summary)
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

1. **Use `/pipeline` endpoint** for batch processing - it does everything automatically!
2. **Use `/ingest-transcript`** for real-time call ingestion
3. **Always validate JSON** before sending
4. **Save analysis results** for summary generation
5. **Monitor system stats** regularly
6. **Test with sample data** before production use
7. **📊 Use analysis history** to track trends and patterns over time
8. **📈 Check analysis statistics** regularly to monitor system performance
9. **💾 Create backups** before clearing analysis data
10. **🔍 Filter analysis history** by date, status, or call ID for targeted insights

---

## 🚀 **Quick Start with Pipeline**

For most use cases, you only need the **`/pipeline`** endpoint:

```bash
# 1. Start the server
uvicorn main:app --reload

# 2. Test the complete pipeline
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d @examples/batch_test.json

# 3. Check the results in the `data/` directory
```

That's it! The pipeline does everything automatically. 🎉 