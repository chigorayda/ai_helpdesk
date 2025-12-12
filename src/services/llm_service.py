"""
LLM service for interacting with Google Gemini and OpenAI.
"""
import time
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from config.settings import settings
from src.models.schemas import LLMProvider

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations using Google Gemini and OpenAI."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self._setup_providers()
        
    def _setup_providers(self):
        """Setup LLM providers."""
        # Setup Gemini
        if settings.google_api_key:
            print("Configuring Google Gemini LLM...")
            genai.configure(api_key=settings.google_api_key)
            self.gemini_llm = GoogleGenerativeAI(
                model=settings.system_config.llm.model_name,
                temperature=settings.system_config.llm.temperature,
                max_tokens=settings.system_config.llm.max_tokens,
                google_api_key=settings.google_api_key
            )
            self.gemini_embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.system_config.vector_store.embedding_model,
                google_api_key=settings.google_api_key
            )
        
        # Setup OpenAI
        if settings.openai_api_key:
            # Note: Using explicit args to avoid pydantic issues with recent langchain versions
            print("Configuring OpenAI LLM...")
            self.openai_llm = ChatOpenAI(
                model=settings.system_config.llm.openai_model_name,
                temperature=settings.system_config.llm.temperature,
                max_tokens=settings.system_config.llm.max_tokens,
                openai_api_key=settings.openai_api_key
            )
            self.openai_embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key
            )
            
        # Set default provider
        self.provider = settings.system_config.llm.provider
        
    def get_llm(self, provider: Optional[LLMProvider] = None):
        """Get the specified LLM instance."""
        target_provider = provider or self.provider
        
        if target_provider == LLMProvider.OPENAI:
            if not hasattr(self, 'openai_llm'):
                raise ValueError("OpenAI API key not configured")
            return self.openai_llm
        else:
            if not hasattr(self, 'gemini_llm'):
                raise ValueError("Google API key not configured")
            return self.gemini_llm

    def get_embeddings(self, texts: list[str], provider: Optional[LLMProvider] = None) -> list[list[float]]:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            provider: Optional provider override
            
        Returns:
            List of embedding vectors
        """
        try:
            start_time = time.time()
            target_provider = provider or self.provider
            
            if target_provider == LLMProvider.OPENAI:
                if not hasattr(self, 'openai_embeddings'):
                    raise ValueError("OpenAI API key not configured")
                embeddings = self.openai_embeddings.embed_documents(texts)
            else:
                if not hasattr(self, 'gemini_embeddings'):
                    raise ValueError("Google API key not configured")
                embeddings = self.gemini_embeddings.embed_documents(texts)
                
            processing_time = time.time() - start_time
            logger.info(f"Generated embeddings for {len(texts)} texts using {target_provider} in {processing_time:.2f}s")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def get_embedding(self, text: str, provider: Optional[LLMProvider] = None) -> list[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            provider: Optional provider override
            
        Returns:
            Embedding vector
        """
        try:
            target_provider = provider or self.provider
            
            if target_provider == LLMProvider.OPENAI:
                if not hasattr(self, 'openai_embeddings'):
                    raise ValueError("OpenAI API key not configured")
                embedding = self.openai_embeddings.embed_query(text)
            else:
                if not hasattr(self, 'gemini_embeddings'):
                    raise ValueError("Google API key not configured")
                embedding = self.gemini_embeddings.embed_query(text)
                
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

            if target_provider == LLMProvider.OPENAI:
                response = await llm.ainvoke(messages)
                text = response.content
            else:
                response = await llm.agenerate([messages])
                text = response.generations[0][0].text
            
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

            if target_provider == LLMProvider.OPENAI:
                 response = llm.invoke(messages)
                 text = response.content
            else:
                # Gemini/LangChain Google GenAI specific
                full_prompt = ""
                if system_message:
                    full_prompt += f"System: {system_message}\n\n"
                full_prompt += f"User: {prompt}\n\nAssistant:"
                text = llm.invoke(full_prompt)
            
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