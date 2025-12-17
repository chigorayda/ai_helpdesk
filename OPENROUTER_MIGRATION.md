# OpenRouter Migration Summary

## Overview
The AI Help Desk System has been migrated from using direct Google Gemini and OpenAI APIs to using **OpenRouter**, which provides unified access to multiple LLM providers with a single API key. Additionally, embeddings now use **Sentence Transformers** (local, free) instead of paid API services.

## Key Changes

### 1. **LLM Providers**
**Before:**
- Google Gemini (via Google API)
- OpenAI GPT-3.5 Turbo (via OpenAI API)

**After (via OpenRouter):**
- **Claude 3.5 Sonnet** (`anthropic/claude-3.5-sonnet`)
- **GPT-4o Mini** (`openai/gpt-4o-mini`)
- **Gemini 2.0 Flash** (`google/gemini-2.0-flash-exp:free`) - Free tier available

### 2. **Embeddings**
**Before:** OpenAI Embeddings or Google Embeddings (paid APIs)

**After:** Sentence Transformers `all-MiniLM-L6-v2` (local, free, no API calls)

### 3. **API Configuration**
**New Required Environment Variable:**
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Removed:**
- `GOOGLE_API_KEY` (no longer needed)
- `OPENAI_API_KEY` (optional, only if you want OpenAI embeddings instead of Sentence Transformers)

### 4. **Model Selection in API**
**Before:**
```json
{
  "request": "I forgot my password",
  "user_id": "user_001",
  "model": "gemini"  // or "openai"
}
```

**After:**
```json
{
  "request": "I forgot my password",
  "user_id": "user_001",
  "model": "claude"  // or "gpt4o-mini" or "gemini"
}
```

### 5. **Comparison Endpoint Enhanced**
**Before:** `/process/compare` compared 2 models (Gemini vs OpenAI)

**After:** `/process/compare` now compares **3 models** (Claude vs GPT-4o Mini vs Gemini)

**Response Structure:**
```json
{
  "request_id": "...",
  "original_request": "...",
  "claude_metrics": { ... },
  "gpt4o_mini_metrics": { ... },
  "gemini_metrics": { ... },
  "claude_response": { ... },
  "gpt4o_mini_response": { ... },
  "gemini_response": { ... },
  "winner": "claude"  // Best performing model
}
```

## Files Modified

### Core Service Files
1. **`src/services/llm_service.py`**
   - Complete rewrite to use OpenRouter for all models
   - Changed from Google/OpenAI specific clients to unified ChatOpenAI interface
   - Added Sentence Transformers for embeddings
   - All models use same API pattern via OpenRouter

2. **`src/services/vector_store.py`**
   - Updated to use Sentence Transformers embeddings
   - Removed provider-specific embedding selection

3. **`src/services/cost_service.py`**
   - Updated pricing for Claude, GPT-4o Mini, and Gemini
   - Gemini 2.0 Flash shows $0 cost (free tier)

### Configuration Files
4. **`config/settings.py`**
   - Changed from `GOOGLE_API_KEY` to `OPENROUTER_API_KEY`
   - Added model configuration for all three providers
   - Updated validation to check for OpenRouter API key

5. **`src/models/schemas.py`**
   - Updated `LLMProvider` enum:
     - `GEMINI` → stays but now via OpenRouter
     - `OPENAI` → `GPT4O_MINI` and `CLAUDE`
   - Updated `LLMConfig` with new model names
   - Updated `ComparisonResponse` for 3-way comparison

### API Files
6. **`app.py`**
   - Updated model validation pattern to accept `claude`, `gpt4o-mini`, `gemini`
   - Updated model mapping in `/process` and `/process/batch` endpoints
   - Enhanced `/process/compare` documentation
   - Updated sample requests with new model names

7. **`main.py`**
   - Completely rewrote `compare_providers()` to compare 3 models
   - Updated `get_system_status()` to show all three model configurations
   - Fixed provider parameter handling in `process_request_sync()`

### Documentation Files
8. **`.env.example`** (NEW)
   - Complete example environment configuration
   - Shows OpenRouter setup
   - Lists all three models

9. **`requirements.txt`**
   - Already had `sentence-transformers==2.2.2`
   - Upgraded to `5.2.0` to fix compatibility issues

## Setup Instructions

### 1. Get OpenRouter API Key
Visit https://openrouter.ai/keys and create an account to get your API key.

### 2. Update .env File
```bash
# Required
OPENROUTER_API_KEY=your_key_here

# Optional (remove if not needed)
OPENAI_API_KEY=  # Only if you want OpenAI embeddings

# Model configurations (defaults shown)
CLAUDE_MODEL=anthropic/claude-3.5-sonnet
GPT4O_MINI_MODEL=openai/gpt-4o-mini
GEMINI_MODEL=google/gemini-2.0-flash-exp:free
```

### 3. Install/Upgrade Dependencies
```bash
source venv/bin/activate
pip install --upgrade sentence-transformers huggingface-hub
```

### 4. Start the Application
```bash
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## Benefits

### Cost Savings
- **Gemini 2.0 Flash**: Free tier available via OpenRouter
- **Embeddings**: Completely free using local Sentence Transformers
- **Unified Billing**: All LLM costs in one place via OpenRouter

### Flexibility
- **Single API Key**: Access 3 different model families
- **Easy Model Switching**: Change models per request without reconfiguration
- **Model Comparison**: Built-in 3-way comparison endpoint

### Performance
- **Claude 3.5 Sonnet**: Best for complex reasoning and nuanced responses
- **GPT-4o Mini**: Fast, cost-effective, good for standard queries
- **Gemini 2.0 Flash**: Free, fast, good for simple queries

### Privacy
- **Local Embeddings**: No external API calls for document embeddings
- **No Vendor Lock-in**: Easy to add more models via OpenRouter

## API Usage Examples

### Process with Specific Model
```bash
# Claude
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{"request": "I forgot my password", "user_id": "user_001", "model": "claude"}'

# GPT-4o Mini
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{"request": "Install Office", "user_id": "user_002", "model": "gpt4o-mini"}'

# Gemini (Free)
curl -X POST http://localhost:8001/process \
  -H 'Content-Type: application/json' \
  -d '{"request": "Network issue", "user_id": "user_003", "model": "gemini"}'
```

### Compare All Three Models
```bash
curl -X POST http://localhost:8001/process/compare \
  -H 'Content-Type: application/json' \
  -d '{"request": "I think I received a phishing email", "user_id": "user_004"}'
```

## Migration Checklist

- [x] Update `llm_service.py` to use OpenRouter
- [x] Add Sentence Transformers for embeddings
- [x] Update `schemas.py` with new provider enum
- [x] Update `settings.py` for OpenRouter config
- [x] Update `cost_service.py` with new pricing
- [x] Update API endpoints to accept new model names
- [x] Update comparison endpoint for 3 models
- [x] Create `.env.example` with new configuration
- [x] Update sample requests with new model names
- [x] Test imports and dependencies
- [ ] Update README.md with OpenRouter info
- [ ] Update API_USAGE.md with new examples
- [ ] Update WARP.md with new architecture details

## Known Issues & Solutions

### Issue 1: sentence-transformers Import Error
**Error:** `ImportError: Could not import sentence_transformers`

**Solution:**
```bash
pip install --upgrade sentence-transformers huggingface-hub
```

### Issue 2: LLMProvider.OPENAI not found
**Error:** `AttributeError: type object 'LLMProvider' has no attribute 'OPENAI'`

**Solution:** All references updated to use `CLAUDE`, `GPT4O_MINI`, or `GEMINI`

## Next Steps

1. **Test the Application**: Start the app and test all three models
2. **Update Documentation**: Update README.md and API_USAGE.md
3. **Performance Testing**: Compare response times and quality across models
4. **Cost Monitoring**: Track actual costs via OpenRouter dashboard
5. **Model Optimization**: Fine-tune which model to use for which request types
