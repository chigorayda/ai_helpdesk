"""
Data models and schemas for the AI Help Desk system.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RequestCategory(str, Enum):
    """Available request categories."""
    PASSWORD_RESET = "password_reset"
    SOFTWARE_INSTALLATION = "software_installation"
    HARDWARE_FAILURE = "hardware_failure"
    NETWORK_CONNECTIVITY = "network_connectivity"
    EMAIL_CONFIGURATION = "email_configuration"
    SECURITY_INCIDENT = "security_incident"
    POLICY_QUESTION = "policy_question"
    UNKNOWN = "unknown"


class PriorityLevel(str, Enum):
    """Priority levels for requests."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HelpDeskRequest(BaseModel):
    """Model for incoming help desk requests."""
    id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    request: str = Field(..., description="User's request text")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ClassificationResult(BaseModel):
    """Result of request classification."""
    category: RequestCategory = Field(..., description="Classified category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    reasoning: str = Field(..., description="Explanation for classification")
    keywords: List[str] = Field(default_factory=list, description="Key terms identified")


class KnowledgeDocument(BaseModel):
    """Model for knowledge base documents."""
    id: str = Field(..., description="Document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    category: Optional[RequestCategory] = Field(None, description="Related category")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    source: str = Field(..., description="Source file path")
    last_updated: datetime = Field(default_factory=datetime.now)


class RetrievalResult(BaseModel):
    """Result from knowledge base retrieval."""
    documents: List[KnowledgeDocument] = Field(..., description="Retrieved documents")
    relevance_scores: List[float] = Field(..., description="Relevance scores")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total number of results")


class EscalationDecision(BaseModel):
    """Decision on whether to escalate a request."""
    should_escalate: bool = Field(..., description="Whether to escalate")
    reasoning: str = Field(..., description="Reason for escalation decision")
    priority: PriorityLevel = Field(..., description="Assigned priority level")
    suggested_department: Optional[str] = Field(None, description="Suggested department")
    estimated_complexity: str = Field(..., description="Complexity assessment")


class HelpDeskResponse(BaseModel):
    """Final response from the help desk system."""
    request_id: str = Field(..., description="Original request ID")
    category: RequestCategory = Field(..., description="Classified category")
    response: str = Field(..., description="Generated response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    knowledge_sources: List[str] = Field(default_factory=list, description="Source documents")
    escalation: EscalationDecision = Field(..., description="Escalation decision")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowState(BaseModel):
    """State object for the LangGraph workflow."""
    request: HelpDeskRequest
    classification: Optional[ClassificationResult] = None
    retrieval_result: Optional[RetrievalResult] = None
    response: Optional[str] = None
    escalation: Optional[EscalationDecision] = None
    errors: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class AgentResponse(BaseModel):
    """Generic response from any agent."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    processing_time: float = Field(..., description="Time taken to process")


# Configuration models
class VectorStoreConfig(BaseModel):
    """Configuration for vector store."""
    collection_name: str = "helpdesk_knowledge"
    embedding_model: str = "models/embedding-001"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    persist_directory: str = "./data/vector_store"


class LLMProvider(str, Enum):
    """Available LLM providers via OpenRouter."""
    CLAUDE = "claude"  # Claude 3.5 Sonnet
    CLAUDE_SONNET_45 = "claude-sonnet-45"  # Claude Sonnet 4.5
    GPT4O_MINI = "gpt4o-mini"  # GPT-4o Mini
    GPT_52 = "gpt-52"  # GPT-5.2
    GEMINI = "gemini"  # Gemini 2.0 Flash
    GEMINI_3_PRO = "gemini-3-pro"  # Gemini 3 Pro Preview
    GROK_4_FAST = "grok-4-fast"  # Grok 4 Fast
    DEEPSEEK_V32 = "deepseek-v32"  # DeepSeek V3.2
    QWEN3_235B = "qwen3-235b"  # Qwen3 235B A22B Instruct 2507
    LLAMA_31_8B = "llama-31-8b"  # Llama 3.1 8B Instruct


class LLMConfig(BaseModel):
    """Configuration for LLM service."""
    provider: LLMProvider = LLMProvider.CLAUDE
    claude_model: str = "anthropic/claude-3.5-sonnet"
    claude_sonnet_45_model: str = "anthropic/claude-sonnet-4.5"
    gpt4o_mini_model: str = "openai/gpt-4o-mini"
    gpt_52_model: str = "openai/gpt-5.2"
    gemini_model: str = "google/gemini-2.0-flash-exp:free"
    gemini_3_pro_model: str = "google/gemini-3-pro-preview"
    grok_4_fast_model: str = "x-ai/grok-4-fast"
    deepseek_v32_model: str = "deepseek/deepseek-chat-v3.2"
    qwen3_235b_model: str = "qwen/qwen3-235b-a22b-instruct-2507"
    llama_31_8b_model: str = "meta-llama/llama-3.1-8b-instruct"
    temperature: float = 0.1
    max_tokens: int = 2000
    timeout: int = 30
    openrouter_api_key: Optional[str] = None

class SystemConfig(BaseModel):
    """Overall system configuration."""
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    knowledge_base_path: str = "./data/knowledge_base"
    escalation_threshold: float = 0.7
    min_confidence_threshold: float = 0.5

class ComparisonMetrics(BaseModel):
    """Metrics for comparing LLM providers."""
    provider: LLMProvider
    processing_time: float
    estimated_cost: float
    hallucination_score: float = 0.0
    response_quality: float = 0.0


class ComparisonResponse(BaseModel):
    """Response comparing different LLM providers."""
    request_id: str
    original_request: str
    providers: List[LLMProvider]  # List of providers compared
    metrics: Dict[str, ComparisonMetrics]  # provider_name -> metrics
    responses: Dict[str, HelpDeskResponse]  # provider_name -> response
    winner: LLMProvider
