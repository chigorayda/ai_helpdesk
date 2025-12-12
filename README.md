# AI Help Desk System

A multi-agent AI help desk system built with LangChain and LangGraph that automatically classifies, processes, and responds to IT support requests.  

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for classification, knowledge retrieval, response generation, and escalation
- **Intelligent Classification**: Categorizes requests into 7 predefined types with confidence scoring
- **RAG-Powered Knowledge Base**: Searches and retrieves relevant information from markdown, JSON, and PDF documents
- **Smart Escalation Logic**: Determines when human intervention is needed based on multiple factors
- **LangGraph Workflow**: Orchestrates agents using state-based workflow management
- **Dual LLM Support**: Choose between Google Gemini and OpenAI per request
- **Provider Comparison**: Benchmark both LLM providers side-by-side
- **Vector Search**: ChromaDB-powered semantic search for knowledge retrieval
- **RESTful API**: FastAPI-powered endpoints with interactive documentation

## 📁 Project Structure

```
ai_helpdesk/
├── README.md
├── requirements.txt
├── .env
├── main.py                 # Main application Orchestration
├── app.py                  # Application entry point
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── src/
│   ├── agents/             # Specialized AI agents
│   │   ├── classifier_agent.py
│   │   ├── knowledge_agent.py
│   │   ├── response_agent.py
│   │   └── escalation_agent.py
│   ├── models/
│   │   └── schemas.py      # Data models and schemas
│   ├── services/           # Core services
│   │   ├── vector_store.py
│   │   ├── document_processor.py
│   │   └── llm_service.py
│   ├── workflows/
│   │   └── helpdesk_workflow.py  # LangGraph workflow
│   └── utils/
│       └── helpers.py      # Utility functions
├── data/
│   ├── knowledge_base/     # Your knowledge base documents
│   └── vector_store/       # Vector embeddings storage
├── tests/
│   └── test_integration.py # Integration tests
└── logs/                   # Application logs
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Google API Key (for Gemini) — required
- OpenAI API Key — optional (for OpenAI provider and comparisons)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_helpdesk
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Google API key and other settings
   ```

   or create the .env file with the following parameter

   ```bash
        # Google API Configuration (Required)
        GOOGLE_API_KEY=your_google_api_key_here

        # OpenAI API Configuration (Optional)
        OPENAI_API_KEY=your_openai_api_key_here

        # Environment Settings
        ENVIRONMENT=development
        DEBUG=true
        LOG_LEVEL=INFO

        # LLM Configuration
        GEMINI_MODEL=gemini-2.0-flash
        OPENAI_MODEL=gpt-3.5-turbo
        LLM_TEMPERATURE=0.1
        MAX_TOKENS=2000

        # Vector Store Configuration
        VECTOR_STORE_PATH=./data/vector_store
        EMBEDDING_MODEL=models/embedding-001

        # Knowledge Base Configuration
        KNOWLEDGE_BASE_PATH=./data/knowledge_base

        # System Thresholds
        ESCALATION_THRESHOLD=0.7
        MIN_CONFIDENCE_THRESHOLD=0.5
   ```


5. **Set up directory structure**
   ```bash
   mkdir -p data/knowledge_base/{faqs,procedures,policies}
   ```

6. **Add your knowledge base documents**
   Place your FAQ files, procedures, and policies in the `data/knowledge_base/` subdirectories.

7. **Start the app**
   ```bash
   # Start with auto-reload (development)
   uvicorn app:app --host 0.0.0.0 --port 8001 --reload

   # Or start without reload (production-like)
   uvicorn app:app --host 0.0.0.0 --port 8001
   ```
The API will be available at:
- API Base URL: http://localhost:8001
- Interactive Docs: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

> For detailed API examples, see [API_USAGE.md](API_USAGE.md)

## 📚 Request Categories

The system automatically classifies requests into these categories:

- **password_reset**: Password and login issues
- **software_installation**: Software installation and licensing
- **hardware_failure**: Hardware problems and repairs
- **network_connectivity**: Internet and network issues
- **email_configuration**: Email setup and configuration
- **security_incident**: Security breaches and suspicious activities
- **policy_question**: Company policy and procedure questions

## 🚀 Usage

### Single Request with Model Selection

```bash
# Gemini (default)
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{"request": "I forgot my password", "user_id": "user_001", "model": "gemini"}'

# OpenAI
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{"request": "Install Microsoft Office", "user_id": "user_002", "model": "openai"}'
```

### Batch Request with Mixed Models

```bash
curl -X POST http://localhost:8001/process/batch \
  -H 'Content-Type: application/json' \
  -d '{"requests": [{"request": "I forgot my password", "user_id": "user_001", "model": "gemini"}, {"request": "My printer is not working", "user_id": "user_003", "model": "openai"}]}'
```

### Compare Providers

```bash
curl -X POST http://localhost:8001/process/compare \
  -H 'Content-Type: application/json' \
  -d '{"request": "I think I received a phishing email", "user_id": "user_003"}'
```

### Single Request

```bash
curl -X 'POST' \
  'http://localhost:8000/process' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "request": " I have been logged out of my system and can'\''t login. What can I do?",
  "user_id": "user_001"
}'
```

### Batch Request

```bash
curl -X 'POST' \
  'http://localhost:8000/process/batch' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "requests": [
{
  "request": "I think I have a phishing attack",
  "user_id": "user_002"
},
{
  "request": " I have been logged out of my system and can'\''t login. What can I do?",
  "user_id": "user_001"
}
  ]
}'
```

## 🧠 How It Works

### Multi-Agent Workflow

1. **Classification Agent**: Analyzes the request and categorizes it
2. **Knowledge Agent**: Searches for relevant information in the knowledge base
3. **Response Agent**: Generates a contextual response using retrieved knowledge
4. **Escalation Agent**: Determines if human intervention is needed

### LangGraph Orchestration

The system uses LangGraph to manage the workflow state and coordinate between agents:

```
┌─────────┐     ┌────────────┐     ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐     ┌──────┐
│ Request │ ──▶ │ Classifier │ ──▶ │ Knowledge Retriever │ ──▶ │ Response Generator │ ──▶ │ Escalation Decision │ ──▶ │ End  │
└─────────┘     └────────────┘     └────────────────────┘     └────────────────────┘     └────────────────────┘     └──────┘
      │                  │                   │                          │                          │
      ▼                  ▼                   ▼                          ▼                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                            Error Handler (fallbacks, retries, logs)                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Knowledge Base Processing

- **Supported Formats**: Markdown (.md), JSON (.json), Text (.txt), PDF (.pdf)
- **Automatic Processing**: Documents are automatically chunked and embedded
- **Semantic Search**: Uses vector similarity for relevant document retrieval
- **Metadata Extraction**: Automatically extracts categories and tags

## ⚙️ Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (with defaults)
GEMINI_MODEL=gemini-1.5-flash
LLM_TEMPERATURE=0.1
ESCALATION_THRESHOLD=0.7
MIN_CONFIDENCE_THRESHOLD=0.5
```

### Escalation Rules

Customize escalation behavior in `config/settings.py`:

```python
ESCALATION_RULES = {
    "security_incident": {
        "auto_escalate": True,
        "priority": "critical",
        "department": "security_team"
    },
    # ... other categories
}
```

## 📊 Response Format

```python
{
    "request_id": "req_12345",
    "category": "password_reset",
    "response": "To reset your password, please visit...",
    "confidence": 0.95,
    "knowledge_sources": ["password_faq.md"],
    "escalation": {
        "should_escalate": False,
        "reasoning": "High confidence self-service solution",
        "priority": "low",
        "suggested_department": "it_support"
    },
    "processing_time": 2.34
}
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_integration.py -v
```

## 📈 Performance Considerations

- **Processing Time**: Typical requests process in 10-15 seconds
- **Knowledge Base Size**: Optimized for 100-10,000 documents
- **Concurrent Requests**: Supports multiple simultaneous requests
- **Memory Usage**: ~200-500MB depending on knowledge base size

## 🔧 Customization

### Adding New Categories

1. Update `RequestCategory` enum in `src/models/schemas.py`
2. Add examples in `config/settings.py`
3. Update escalation rules if needed

### Knowledge Base Sources

The system can process:
- **Markdown files**: FAQs, procedures, guides
- **JSON files**: Structured knowledge with metadata
- **PDF files**: Policy documents, manuals
- **Text files**: Simple documentation

## 🚨 Troubleshooting
### Common Issues

1. **"No documents found"**: Check `data/knowledge_base/` directory
2. **"API key error"**: Verify `GOOGLE_API_KEY` in `.env`
3. **"Low response quality"**: Add more relevant documents to knowledge base
4. **"Slow processing"**: Reduce knowledge base size or increase chunk size

## 📚 Documentation

- [API_USAGE.md](API_USAGE.md): Comprehensive API usage guide with examples
- [WARP.md](WARP.md): Development guidance for contributors
- Interactive Docs: http://localhost:8001/docs

## 🔮 Further Improvements
1. Include a Database to persist requests and responses
2. Include Docker & Docker Compose for deployment and scalability
3. Add monitoring to track LLM performance metrics
4. Implement caching for repeated queries
5. Add support for more LLM providers (e.g., Claude)

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the AI framework
- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [Google Gemini](https://ai.google.dev/) for language model capabilities


**Contact**: Chigozilai Kejeh ~ kebochig@gmail.com