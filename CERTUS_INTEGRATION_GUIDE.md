# 🔗 Certus Integration Guide

A comprehensive guide for integrating Certus with the Call Replay Analyzer to automatically ingest and analyze failed calls.

## 🎯 Overview

This integration allows Certus to automatically send failed call transcripts to the Call Replay Analyzer via webhooks. When a call fails in Certus, it will automatically trigger the webhook, which will:

1. ✅ **Receive the failed call transcript**
2. ✅ **Process it in the background** (non-blocking)
3. ✅ **Analyze the call** using AI
4. ✅ **Store results** for later review
5. ✅ **Generate insights** about the failure

## 🚀 Quick Setup

### Step 1: Configure Certus Webhook

In your Certus dashboard, configure the webhook with these settings:

**Webhook URL:**
```
http://your-server:8000/webhook
```

**HTTP Method:** `POST`

**Content-Type:** `application/json`

**Trigger Conditions:**
- Call status = "failed"
- Call duration > 30 seconds
- Customer satisfaction = "low"
- Intent recognition failed

### Step 2: Configure Payload Format

Certus should send the following JSON payload:

```json
{
  "call_id": "certus_call_12345",
  "dialog": [
    {
      "speaker": "user",
      "text": "Do you deliver to Bandra?",
      "timestamp": "2024-01-15T14:30:00Z"
    },
    {
      "speaker": "bot", 
      "text": "We are open 11 to 10.",
      "timestamp": "2024-01-15T14:30:05Z"
    },
    {
      "speaker": "user",
      "text": "That's not what I asked!",
      "timestamp": "2024-01-15T14:30:10Z"
    }
  ],
  "metadata": {
    "certus_call_id": "certus_12345",
    "failure_reason": "intent_misunderstanding",
    "call_duration": 45,
    "customer_satisfaction": "low",
    "restaurant_id": "rest_001",
    "customer_id": "cust_456",
    "call_timestamp": "2024-01-15T14:30:00Z",
    "certus_confidence_score": 0.3
  }
}
```

### Step 3: Test the Integration

Use this test payload to verify the webhook is working:

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_certus_call_001",
    "dialog": [
      {"speaker": "user", "text": "Do you deliver to Bandra?"},
      {"speaker": "bot", "text": "We are open 11 to 10."},
      {"speaker": "user", "text": "That'\''s not what I asked!"}
    ],
    "metadata": {
      "certus_call_id": "certus_test_001",
      "failure_reason": "intent_misunderstanding",
      "call_duration": 45,
      "customer_satisfaction": "low"
    }
  }'
```

Expected response:
```json
{
  "status": "received",
  "call_id": "test_certus_call_001",
  "message": "Call transcript queued for analysis",
  "webhook_id": "webhook_1705312345_test_certus_call_001",
  "timestamp": 1705312345.123
}
```

## 📋 Detailed Configuration

### Certus Webhook Settings

#### Basic Configuration
- **URL**: `http://your-server:8000/webhook`
- **Method**: `POST`
- **Headers**: 
  - `Content-Type: application/json`
  - `User-Agent: Certus-Webhook/1.0`

#### Trigger Conditions
Configure Certus to trigger the webhook when:

```javascript
// Example Certus trigger logic
if (
  call.status === "failed" ||
  call.customer_satisfaction === "low" ||
  call.intent_confidence < 0.5 ||
  call.duration > 60
) {
  // Send webhook
  sendWebhook(call);
}
```

#### Retry Logic
- **Max Retries**: 3
- **Retry Delay**: 5 seconds, 15 seconds, 30 seconds
- **Timeout**: 10 seconds

### Payload Structure

#### Required Fields
- `call_id`: Unique identifier for the call
- `dialog`: Array of conversation turns
- `metadata`: Additional call information

#### Dialog Format
Each dialog turn should have:
- `speaker`: "user" or "bot"
- `text`: The spoken text
- `timestamp`: ISO 8601 timestamp (optional)

#### Metadata Fields
Recommended metadata fields:
- `certus_call_id`: Original Certus call ID
- `failure_reason`: Why the call failed
- `call_duration`: Call duration in seconds
- `customer_satisfaction`: "high", "medium", "low"
- `restaurant_id`: Restaurant identifier
- `customer_id`: Customer identifier
- `call_timestamp`: When the call occurred
- `certus_confidence_score`: Certus confidence score

## 🔍 Monitoring and Debugging

### Check Webhook Status

#### 1. View Recent Webhooks
```bash
curl "http://localhost:8000/analysis-history?status=analyzed&limit=10"
```

#### 2. Check Webhook Statistics
```bash
curl http://localhost:8000/analysis-stats
```

#### 3. View Specific Call Analysis
```bash
curl http://localhost:8000/analysis-history/certus_call_12345
```

### Log Monitoring

The system logs webhook activity with these patterns:

```
🔗 Certus webhook received for call: certus_call_12345
🔄 Processing Certus webhook call: certus_call_12345
✅ Certus call certus_call_12345 analyzed successfully
🚨 Issues detected in Certus call certus_call_12345: intent_misunderstanding
✅ Certus webhook processing completed for call: certus_call_12345
```

### Error Handling

#### Common Issues

1. **Timeout Errors**
   - Increase Certus webhook timeout to 15 seconds
   - Check server performance

2. **Payload Format Errors**
   - Validate JSON structure
   - Check required fields

3. **Network Issues**
   - Verify server accessibility
   - Check firewall settings

#### Debug Commands

```bash
# Test webhook connectivity
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"call_id": "test", "dialog": []}'

# Check server health
curl http://localhost:8000/health

# View recent errors
curl "http://localhost:8000/analysis-history?status=error&limit=5"
```

## 📊 Data Flow

### 1. Call Failure in Certus
```
Customer Call → Certus Processing → Call Fails → Webhook Triggered
```

### 2. Webhook Processing
```
Webhook Received → Background Processing → Analysis → Storage
```

### 3. Results Available
```
Analysis Complete → Results Stored → Available via API → Dashboard Ready
```

## 🎯 Use Cases

### Real-time Failure Detection
- **Scenario**: Customer calls about delivery
- **Certus**: Bot misunderstands intent
- **Webhook**: Automatically sent to analyzer
- **Result**: Immediate analysis and fix suggestions

### Batch Analysis
- **Scenario**: Multiple failed calls overnight
- **Certus**: Sends webhooks for each failure
- **Analyzer**: Processes all calls
- **Result**: Morning report with all issues

### Trend Analysis
- **Scenario**: Pattern of delivery failures
- **Certus**: Sends webhooks for each failure
- **Analyzer**: Identifies common patterns
- **Result**: Systemic fix recommendations

## 🔧 Advanced Configuration

### Custom Metadata Mapping

Map Certus fields to analyzer metadata:

```javascript
// Certus webhook payload mapping
const webhookPayload = {
  call_id: call.id,
  dialog: call.transcript,
  metadata: {
    certus_call_id: call.certus_id,
    failure_reason: call.failure_reason,
    call_duration: call.duration,
    customer_satisfaction: call.satisfaction,
    restaurant_id: call.restaurant_id,
    customer_id: call.customer_id,
    call_timestamp: call.timestamp,
    certus_confidence_score: call.confidence,
    // Custom fields
    call_type: call.type,
    agent_id: call.agent_id,
    queue_time: call.queue_time
  }
};
```

### Conditional Webhook Triggers

Configure different webhook behaviors:

```javascript
// Different webhook URLs for different failure types
if (call.failure_type === "intent") {
  webhookUrl = "http://analyzer/webhook/intent-failure";
} else if (call.failure_type === "delivery") {
  webhookUrl = "http://analyzer/webhook/delivery-failure";
} else {
  webhookUrl = "http://analyzer/webhook/general-failure";
}
```

## 📈 Performance Considerations

### Webhook Processing
- **Background Processing**: Non-blocking for Certus
- **Immediate Response**: Acknowledgment within 100ms
- **Async Analysis**: Full analysis in background

### Scalability
- **Concurrent Processing**: Multiple webhooks simultaneously
- **Queue Management**: Automatic retry on failures
- **Resource Optimization**: Efficient memory usage

### Monitoring
- **Success Rate**: Track webhook delivery success
- **Processing Time**: Monitor analysis duration
- **Error Rates**: Identify and fix issues quickly

## 🚀 Production Deployment

### Security Considerations
- **HTTPS**: Use HTTPS in production
- **Authentication**: Consider adding webhook authentication
- **Rate Limiting**: Implement rate limiting if needed
- **IP Whitelisting**: Restrict to Certus IP ranges

### High Availability
- **Load Balancing**: Use multiple analyzer instances
- **Failover**: Implement webhook retry logic
- **Monitoring**: Set up alerts for webhook failures
- **Backup**: Regular data backups

### Performance Tuning
- **Database**: Optimize storage for high volume
- **Caching**: Cache frequently accessed data
- **Queue Management**: Implement proper queuing
- **Resource Scaling**: Scale based on webhook volume

## 📞 Support

### Getting Help
1. **Check Logs**: Review server logs for errors
2. **Test Webhook**: Use test payloads to verify
3. **Monitor Health**: Check `/health` endpoint
4. **Contact Support**: For persistent issues

### Troubleshooting Checklist
- [ ] Certus webhook URL is correct
- [ ] Server is accessible from Certus
- [ ] Payload format matches expected structure
- [ ] Required fields are present
- [ ] Network connectivity is stable
- [ ] Server has sufficient resources
- [ ] Logs show successful processing

---

## 🎉 Success Metrics

After integration, you should see:
- ✅ **Automatic webhook delivery** for failed calls
- ✅ **Background processing** without blocking Certus
- ✅ **Stored analysis results** in the system
- ✅ **Actionable insights** from failed calls
- ✅ **Improved bot performance** based on analysis

The integration is now complete! Certus will automatically send failed calls to your analyzer, and you'll get immediate insights into what went wrong and how to fix it. 🚀 