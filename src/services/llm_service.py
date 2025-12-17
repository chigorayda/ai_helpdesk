"""
LLM service for interacting with multiple models via OpenRouter.
"""
import time
import logging
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from config.settings import settings
from src.models.schemas import LLMProvider

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations using OpenRouter."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self._setup_providers()
        
    def _setup_providers(self):
        """Setup LLM providers via OpenRouter."""
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required but not set")
        
        print("Configuring OpenRouter LLMs...")
        
        # Setup Claude 3.5 Sonnet via OpenRouter
        self.claude_llm = ChatOpenAI(
            model=settings.system_config.llm.claude_model,
            temperature=settings.system_config.llm.temperature,
            max_tokens=settings.system_config.llm.max_tokens,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/ai-helpdesk",
                "X-Title": "AI Help Desk System"
            }
        )
        
        # Setup GPT-4o Mini via OpenRouter
        self.gpt4o_mini_llm = ChatOpenAI(
            model=settings.system_config.llm.gpt4o_mini_model,
            temperature=settings.system_config.llm.temperature,
            max_tokens=settings.system_config.llm.max_tokens,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/ai-helpdesk",
                "X-Title": "AI Help Desk System"
            }
        )
        
        # Setup Gemini 2.0 Flash via OpenRouter
        self.gemini_llm = ChatOpenAI(
            model=settings.system_config.llm.gemini_model,
            temperature=settings.system_config.llm.temperature,
            max_tokens=settings.system_config.llm.max_tokens,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/ai-helpdesk",
                "X-Title": "AI Help Desk System"
            }
        )
        
        # Setup embeddings using Sentence Transformers (local, free)
        print("Initializing Sentence Transformers embeddings...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("Embeddings initialized with all-MiniLM-L6-v2")
            
        # Set default provider
        self.provider = settings.system_config.llm.provider
        
        print(f"OpenRouter configured with Claude, GPT-4o Mini, and Gemini 2.0 Flash")
        print(f"Default provider: {self.provider.value}")
        
    def get_llm(self, provider: Optional[LLMProvider] = None):
        """Get the specified LLM instance."""
        target_provider = provider or self.provider
        
        if target_provider == LLMProvider.CLAUDE:
            return self.claude_llm
        elif target_provider == LLMProvider.GPT4O_MINI:
            return self.gpt4o_mini_llm
        elif target_provider == LLMProvider.GEMINI:
            return self.gemini_llm
        else:
            raise ValueError(f"Unknown provider: {target_provider}")

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for a list of texts using Sentence Transformers.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            start_time = time.time()
            embeddings = self.embeddings.embed_documents(texts)
            processing_time = time.time() - start_time
            logger.info(f"Generated embeddings for {len(texts)} texts using Sentence Transformers in {processing_time:.2f}s")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def get_embedding(self, text: str) -> list[float]:
        """
        Get embedding for a single text using Sentence Transformers.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        provider: Optional[LLMProvider] = None
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message
            temperature: Optional temperature override
            provider: Optional provider override
            
        Returns:
            Generated response text
        """
        try:
            start_time = time.time()
            target_provider = provider or self.provider
            llm = self.get_llm(target_provider)
            
            # Prepare messages
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            # Handle temperature override
            if temperature is not None:
                # This is a simplified approach; in production you might clone the LLM config
                # For now we rely on the default config or separate instantiation if needed
                pass

            # All providers use ChatOpenAI interface via OpenRouter
            response = await llm.ainvoke(messages)
            text = response.content
            
            processing_time = time.time() - start_time
            logger.info(f"LLM response generated in {processing_time:.2f}s using {target_provider}")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def generate_response_sync(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        provider: Optional[LLMProvider] = None
    ) -> str:
        """
        Synchronous version of generate_response.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message
            temperature: Optional temperature override
            provider: Optional provider override
            
        Returns:
            Generated response text
        """
        try:
            start_time = time.time()
            target_provider = provider or self.provider
            llm = self.get_llm(target_provider)
            
            # Prepare messages/prompt
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))

            # All providers use ChatOpenAI interface via OpenRouter
            response = llm.invoke(messages)
            text = response.content
            
            processing_time = time.time() - start_time
            logger.info(f"LLM response generated in {processing_time:.2f}s using {target_provider}")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def analyze_text_sentiment(self, text: str, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """
        Analyze sentiment and urgency of text.
        
        Args:
            text: Text to analyze
            provider: Optional provider override
            
        Returns:
            Dictionary with sentiment analysis
        """
        prompt = f"""
        Analyze the following help desk request for sentiment, urgency, and tone:
        
        Request: "{text}"
        
        Provide your analysis in the following JSON format:
        {{
            "sentiment": "positive/neutral/negative",
            "urgency": "low/medium/high/critical",
            "tone": "frustrated/calm/confused/angry/polite",
            "confidence": 0.0-1.0,
            "reasoning": "explanation of analysis"
        }}
        
        Only return the JSON, no additional text.
        """
        
        try:
            response = self.generate_response_sync(prompt, temperature=0.1, provider=provider)
            # Parse JSON response
            import json
            # Clean response if needed (remove markdown)
            clean_response = response.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_response)
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {str(e)}")
            return {
                "sentiment": "neutral",
                "urgency": "medium",
                "tone": "unknown",
                "confidence": 0.5,
                "reasoning": "Analysis failed"
            }
    
    def extract_keywords(self, text: str, provider: Optional[LLMProvider] = None) -> list[str]:
        """
        Extract key terms and entities from text.
        
        Args:
            text: Text to analyze
            provider: Optional provider override
            
        Returns:
            List of keywords
        """
        prompt = f"""
        Extract the most important keywords and technical terms from this help desk request:
        
        Request: "{text}"
        
        Return only a comma-separated list of keywords, no additional text.
        Focus on:
        - Technical terms
        - Software/hardware names
        - Actions requested
        - Problem symptoms
        """
        
        try:
            response = self.generate_response_sync(prompt, temperature=0.1, provider=provider)
            keywords = [kw.strip() for kw in response.split(',')]
            return [kw for kw in keywords if kw and len(kw) > 1]
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []


# Global LLM service instance
llm_service = LLMService()