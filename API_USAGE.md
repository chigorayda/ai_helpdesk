# API Usage Guide

This guide provides detailed instructions on how to start the AI Help Desk System and use its API endpoints.

## Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment activated
- Google API key configured (required)
- OpenAI API key configured (optional, for provider comparison)

### 1. Setup Environment

```bash
# Navigate to project directory
cd ai_helpdesk

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Ensure dependencies are installed
pip install -r requirements.txt
```

### 2. Configure API Keys

Create or edit the `.env` file:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for OpenAI comparison)
OPENAI_API_KEY=your_openai_api_key_here

# Optional Configuration
GEMINI_MODEL=gemini-2.0-flash
OPENAI_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1
LOG_LEVEL=INFO
```

### 3. Start the Application

```bash
# Start with auto-reload (development)
uvicorn app:app --host 0.0.0.0 --port 8001 --reload

# Or start without reload (production-like)
uvicorn app:app --host 0.0.0.0 --port 8001
```

The API will be available at:
- **API Base URL**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## API Endpoints

### 1. Health Check

Check if the system is running and initialized.

**Endpoint**: `GET /health`

**Example**:
```bash
curl -X GET http://localhost:8001/health
```

**Response**:
```json
{
  "status": "healthy",
  "initialized": true,
  "timestamp": "2025-12-12T00:00:00.000000"
}
```

---

### 2. System Status

Get detailed system status including knowledge base stats and configuration.

**Endpoint**: `GET /status`

**Example**:
```bash
curl -X GET http://localhost:8001/status
```

**Response**:
```json
{
  "initialized": true,
  "timestamp": "2025-12-12T00:00:00",
  "knowledge_base": {
    "document_count": 19,
    "collection_name": "helpdesk_knowledge"
  },
  "workflow_metrics": {},
  "configuration": {
    "model": "gemini-2.0-flash",
    "temperature": 0.1,
    "escalation_threshold": 0.7,
    "min_confidence_threshold": 0.5
  }
}
```

---

### 3. Process Single Request

Process a help desk request with your choice of LLM provider.

**Endpoint**: `POST /process`

**Request Body**:
```json
{
  "request": "I forgot my password and can't log in",
  "user_id": "user_001",
  "model": "gemini"  // or "openai"
}
```

**Parameters**:
- `request` (required): The user's help desk question
- `user_id` (optional): User identifier
- `model` (optional): LLM provider - `"gemini"` (default) or `"openai"`

**Example with Gemini**:
```bash
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{
    "request": "I forgot my password and can'\''t log in",
    "user_id": "user_001",
    "model": "gemini"
  }'
```

**Example with OpenAI**:
```bash
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{
    "request": "I need to install Microsoft Office",
    "user_id": "user_002",
    "model": "openai"
  }'
```

**Response**:
```json
{
  "request_id": "abc123...",
  "category": "password_reset",
  "response": "To reset your password, please follow these steps:\n1. Go to the login page...",
  "confidence": 0.95,
  "knowledge_sources": [
    "data/knowledge_base/faqs/password_reset.md"
  ],
  "escalation": {
    "should_escalate": false,
    "reasoning": "High confidence self-service solution available",
    "priority": "low",
    "suggested_department": "it_support",
    "estimated_complexity": "simple"
  },
  "processing_time": 11.7,
  "timestamp": "2025-12-12T00:00:00.000000"
}
```

---

### 4. Batch Processing

Process multiple requests at once, with different models per request.

**Endpoint**: `POST /process/batch`

**Request Body**:
```json
{
  "requests": [
    {
      "request": "I forgot my password",
      "user_id": "user_001",
      "model": "gemini"
    },
    {
      "request": "Install Office 365",
      "user_id": "user_002",
      "model": "openai"
    }
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8001/process/batch \
  -H 'Content-Type: application/json' \
  -d '{
    "requests": [
      {
        "request": "I forgot my password",
        "user_id": "user_001",
        "model": "gemini"
      },
      {
        "request": "My printer is not working",
        "user_id": "user_002",
        "model": "openai"
      }
    ]
  }'
```

**Response**: Array of `HelpDeskResponse` objects (same as single request response).

---

### 5. Compare Providers

Process the same request with both Gemini and OpenAI, then compare performance.

**Endpoint**: `POST /process/compare`

**Request Body**:
```json
{
  "request": "I think I received a phishing email",
  "user_id": "user_003"
}
```

**Example**:
```bash
curl -X POST http://localhost:8001/process/compare \
  -H 'Content-Type: application/json' \
  -d '{
    "request": "I think I received a phishing email",
    "user_id": "user_003"
  }'
```

**Response**:
```json
{
  "request_id": "xyz789...",
  "original_request": "I think I received a phishing email",
  "gemini_metrics": {
    "provider": "gemini",
    "processing_time": 12.5,
    "estimated_cost": 0.00015,
    "hallucination_score": 0.0,
    "response_quality": 0.98
  },
  "openai_metrics": {
    "provider": "openai",
    "processing_time": 8.3,
    "estimated_cost": 0.00025,
    "hallucination_score": 0.0,
    "response_quality": 0.95
  },
  "gemini_response": {
    "request_id": "...",
    "category": "security_incident",
    "response": "...",
    "confidence": 0.98,
    "escalation": {
      "should_escalate": true,
      "priority": "critical"
    }
  },
  "openai_response": {
    "request_id": "...",
    "category": "security_incident",
    "response": "...",
    "confidence": 0.95,
    "escalation": {
      "should_escalate": true,
      "priority": "critical"
    }
  },
  "winner": "gemini"
}
```

**Winner Determination**:
- Primarily based on confidence score
- If tied, the lower cost option wins

---

### 6. Knowledge Base Management

#### Get Knowledge Base Stats

**Endpoint**: `GET /knowledge-base/stats`

**Example**:
```bash
curl -X GET http://localhost:8001/knowledge-base/stats
```

**Response**:
```json
{
  "knowledge_base_stats": {
    "document_count": 19,
    "collection_name": "helpdesk_knowledge"
  },
  "timestamp": "2025-12-12T00:00:00.000000"
}
```

#### Refresh Knowledge Base

Reload all documents from the knowledge base directory.

**Endpoint**: `POST /knowledge-base/refresh`

**Example**:
```bash
curl -X POST http://localhost:8001/knowledge-base/refresh
```

**Response**:
```json
{
  "success": true,
  "message": "Knowledge base refresh started in background",
  "timestamp": "2025-12-12T00:00:00.000000"
}
```

---

### 7. Sample Requests

Get example requests for testing.

**Endpoint**: `GET /sample-requests`

**Example**:
```bash
curl -X GET http://localhost:8001/sample-requests
```

**Response**:
```json
{
  "sample_requests": [
    {
      "request": "I forgot my password and can't log into my computer. How do I reset it?",
      "user_id": "user001",
      "model": "gemini"
    },
    {
      "request": "I need to install Microsoft Office on my new laptop. Can you help?",
      "user_id": "user002",
      "model": "openai"
    }
  ]
}
```

---

## Request Categories

The system automatically classifies requests into these categories:

| Category | Description | Example |
|----------|-------------|---------|
| `password_reset` | Password and login issues | "I forgot my password" |
| `software_installation` | Software installation and licensing | "Need to install Office" |
| `hardware_failure` | Hardware problems and repairs | "My printer is not working" |
| `network_connectivity` | Internet and network issues | "Can't connect to WiFi" |
| `email_configuration` | Email setup and configuration | "Email not working" |
| `security_incident` | Security breaches and suspicious activities | "Received phishing email" |
| `policy_question` | Company policy and procedure questions | "What's the VPN policy?" |

---

## Escalation Logic

Requests are automatically escalated based on:

1. **Category Rules**: Security incidents always escalate
2. **Confidence Threshold**: Low confidence (<0.7 by default) triggers escalation
3. **Complexity**: Complex issues that require human expertise

**Escalation Response Fields**:
- `should_escalate`: Boolean indicating if escalation is needed
- `reasoning`: Explanation for the decision
- `priority`: `low`, `medium`, `high`, or `critical`
- `suggested_department`: Which team should handle it
- `estimated_complexity`: Assessment of issue complexity

---

## Model Selection Guide

### When to Use Gemini
- **Faster responses** for simple queries
- **Lower cost** per request
- **Good for**: FAQs, straightforward issues

### When to Use OpenAI
- **Better reasoning** for complex problems
- **More consistent** formatting
- **Good for**: Complex troubleshooting, nuanced issues

### Comparison Endpoint
Use `/process/compare` to:
- Benchmark both models on your specific requests
- Determine which model works best for your use case
- Compare cost vs. quality trade-offs

---

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": "Error message",
  "status_code": 500,
  "timestamp": "2025-12-12T00:00:00.000000"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error
- `503`: Service Unavailable (system not initialized)

---

## Interactive API Documentation

Visit **http://localhost:8001/docs** for:
- Interactive API testing
- Request/response schemas
- Try-it-out functionality
- Detailed parameter descriptions

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8001"

# Process a request
response = requests.post(
    f"{BASE_URL}/process",
    json={
        "request": "I forgot my password",
        "user_id": "user_001",
        "model": "gemini"
    }
)

result = response.json()
print(f"Category: {result['category']}")
print(f"Response: {result['response']}")
print(f"Should Escalate: {result['escalation']['should_escalate']}")
```

---

## Performance Tips

1. **Batch Processing**: Use `/process/batch` for multiple requests to reduce overhead
2. **Model Selection**: Choose Gemini for speed, OpenAI for complex reasoning
3. **Knowledge Base**: Keep documents organized and updated for better responses
4. **Caching**: Results can be cached on the client side for repeated queries

---

## Troubleshooting

### "System not initialized" (503)
- Check logs for initialization errors
- Verify API keys are configured
- Ensure knowledge base directory exists

### "API key error"
- Verify `GOOGLE_API_KEY` in `.env` file
- Check if key is valid and not expired
- For OpenAI, ensure `OPENAI_API_KEY` is set

### Slow responses
- Check network connectivity
- Verify knowledge base size (large databases slow down searches)
- Consider using Gemini for faster responses

### Low confidence scores
- Add more relevant documents to knowledge base
- Improve document quality and structure
- Use more specific keywords in documents

---

## Support

For issues or questions:
- Check the logs at `helpdesk.log`
- Review the main README.md for setup instructions
- See WARP.md for development guidance
