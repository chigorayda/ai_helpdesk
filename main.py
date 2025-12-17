"""
Main application for the AI Help Desk System.
"""
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from config.settings import settings
from src.models.schemas import HelpDeskRequest, HelpDeskResponse
from src.workflows.helpdesk_workflow import helpdesk_workflow
from src.services.document_processor import document_processor
from src.services.vector_store import vector_store_service

from src.services.cost_service import cost_service
from src.models.schemas import ComparisonResponse, ComparisonMetrics, LLMProvider

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('helpdesk.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HelpDeskSystem:
    """Main Help Desk System orchestrator."""
    
    def __init__(self):
        """Initialize the help desk system."""
        self.workflow = helpdesk_workflow
        self.document_processor = document_processor
        self.vector_store = vector_store_service
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the help desk system.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing AI Help Desk System...")
            
            # Validate settings
            settings.validate_settings()
            logger.info("Settings validated successfully")
            
            # Initialize knowledge base
            await self._initialize_knowledge_base()
            
            self.is_initialized = True
            logger.info("AI Help Desk System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize help desk system: {str(e)}")
            return False
    
    def initialize_sync(self) -> bool:
        """
        Synchronous version of initialize.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing AI Help Desk System...")
            
            # Validate settings
            settings.validate_settings()
            logger.info("Settings validated successfully")
            
            # Initialize knowledge base
            self._initialize_knowledge_base_sync()
            
            self.is_initialized = True
            logger.info("AI Help Desk System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize help desk system: {str(e)}")
            return False
    
    async def _initialize_knowledge_base(self):
        """Initialize the knowledge base."""
        try:
            logger.info("Loading knowledge base documents...")
            
            # Load all documents from knowledge base directory
            documents = self.document_processor.load_all_documents()
            
            if documents:
                # Add documents to vector store
                success = self.vector_store.add_documents(documents)
                if success:
                    logger.info(f"Successfully loaded {len(documents)} documents into knowledge base")
                else:
                    logger.warning("Failed to add some documents to vector store")
            else:
                logger.warning("No documents found in knowledge base directory")
                logger.info("You can add documents to the 'data/knowledge_base' directory")
            
            # Get vector store statistics
            stats = self.vector_store.get_collection_stats()
            logger.info(f"Knowledge base stats: {stats}")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            raise
    
    def _initialize_knowledge_base_sync(self):
        """Synchronous version of knowledge base initialization."""
        try:
            logger.info("Loading knowledge base documents...")
            
            # Load all documents from knowledge base directory
            documents = self.document_processor.load_all_documents()
            
            if documents:
                # Add documents to vector store
                success = self.vector_store.add_documents(documents)
                if success:
                    logger.info(f"Successfully loaded {len(documents)} documents into knowledge base")
                else:
                    logger.warning("Failed to add some documents to vector store")
            else:
                logger.warning("No documents found in knowledge base directory")
                logger.info("You can add documents to the 'data/knowledge_base' directory")
            
            # Get vector store statistics
            stats = self.vector_store.get_collection_stats()
            logger.info(f"Knowledge base stats: {stats}")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            raise
    
    async def process_request(self, request_text: str, user_id: str = None) -> HelpDeskResponse:
        """
        Process a help desk request.
        
        Args:
            request_text: The user's request text
            user_id: Optional user identifier
            
        Returns:
            HelpDeskResponse with the result
        """
        if not self.is_initialized:
            raise RuntimeError("Help desk system not initialized. Call initialize() first.")
        
        try:
            # Create request object
            request = HelpDeskRequest(
                id=str(uuid.uuid4()),
                user_id=user_id,
                request=request_text,
                timestamp=datetime.now()
            )
            
            logger.info(f"Processing request {request.id}: {request_text[:100]}...")
            
            # Process through workflow
            response = await self.workflow.process_request(request)
            
            logger.info(f"Request {request.id} processed in {response.processing_time:.2f}s")
            logger.info(f"Category: {response.category.value}, Confidence: {response.confidence:.2f}")
            logger.info(f"Escalation: {'Yes' if response.escalation.should_escalate else 'No'}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise
    
    def process_request_sync(self, request_text: str, user_id: str = None, provider: Optional[LLMProvider] = None) -> HelpDeskResponse:
        """
        Synchronous version of process_request.
        
        Args:
            request_text: The user's request text
            user_id: Optional user identifier
            provider: Optional LLM provider to use (Gemini or OpenAI)
            
        Returns:
            HelpDeskResponse with the result
        """
        if not self.is_initialized:
            raise RuntimeError("Help desk system not initialized. Call initialize_sync() first.")
        
        try:
            # Set provider if specified
            original_provider = settings.system_config.llm.provider
            if provider:
                settings.system_config.llm.provider = provider
                logger.info(f"Using {provider.value} provider for this request")
            
            # Create request object
            request = HelpDeskRequest(
                id=str(uuid.uuid4()),
                user_id=user_id,
                request=request_text,
                timestamp=datetime.now()
            )
            
            logger.info(f"Processing request {request.id}: {request_text[:100]}...")
            
            # Process through workflow
            response = self.workflow.process_request_sync(request)
            
            # Restore original provider
            if provider:
                settings.system_config.llm.provider = original_provider
            
            logger.info(f"Request {request.id} processed in {response.processing_time:.2f}s")
            logger.info(f"Category: {response.category.value}, Confidence: {response.confidence:.2f}")
            logger.info(f"Escalation: {'Yes' if response.escalation.should_escalate else 'No'}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise
    
    def _calculate_hallucination_score(self, confidence: float, num_sources: int, escalated: bool) -> float:
        """
        Calculate a hallucination risk score (0.0 to 1.0, lower is better).
        
        Args:
            confidence: Classification/response confidence (0-1)
            num_sources: Number of knowledge sources used
            escalated: Whether request was escalated
            
        Returns:
            Hallucination score (0.0 = low risk, 1.0 = high risk)
        """
        score = 0.0
        
        # Low confidence increases hallucination risk
        if confidence < 0.5:
            score += 0.5
        elif confidence < 0.7:
            score += 0.3
        elif confidence < 0.85:
            score += 0.1
        
        # No knowledge sources = higher risk of making things up
        if num_sources == 0:
            score += 0.3
        elif num_sources == 1:
            score += 0.1
        
        # Escalated requests might indicate uncertainty
        if escalated:
            score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def batch_process_requests(self, requests: List[Dict[str, str]]) -> List[HelpDeskResponse]:
        """
        Process multiple requests in batch.
        
        Args:
            requests: List of request dictionaries with 'request' and optional 'user_id' and 'provider' keys
            
        Returns:
            List of HelpDeskResponse objects
        """
        if not self.is_initialized:
            raise RuntimeError("Help desk system not initialized. Call initialize_sync() first.")
        
        responses = []
        
        for i, req_data in enumerate(requests):
            try:
                logger.info(f"Processing batch request {i+1}/{len(requests)}")
                
                # Get provider if specified
                provider = req_data.get('provider')
                
                response = self.process_request_sync(
                    request_text=req_data['request'],
                    user_id=req_data.get('user_id'),
                    provider=provider
                )
                responses.append(response)
                
            except Exception as e:
                logger.error(f"Error processing batch request {i+1}: {str(e)}")
                # Create error response
                from src.models.schemas import EscalationDecision, PriorityLevel, RequestCategory
                error_response = HelpDeskResponse(
                    request_id=str(uuid.uuid4()),
                    category=RequestCategory.UNKNOWN,
                    response=f"Error processing request: {str(e)}",
                    confidence=0.0,
                    knowledge_sources=[],
                    escalation=EscalationDecision(
                        should_escalate=True,
                        reasoning=f"Processing error: {str(e)}",
                        priority=PriorityLevel.HIGH,
                        suggested_department="it_support",
                        estimated_complexity="error"
                    ),
                    processing_time=0.0
                )
                responses.append(error_response)
        
        return responses
    
    async def compare_providers(self, request_text: str, user_id: str = None) -> ComparisonResponse:
        """
        Compare Claude, GPT-4o Mini, and Gemini processing for the same request.
        
        Args:
            request_text: The user's request text
            user_id: Optional user identifier
            
        Returns:
            ComparisonResponse with metrics and responses from all three providers
        """
        if not self.is_initialized:
            raise RuntimeError("Help desk system not initialized. Call initialize() first.")

        request_id = str(uuid.uuid4())
        input_tokens = cost_service.estimate_tokens(request_text)
        logger.info(f"Comparison request tokens - Input: {input_tokens}")
        
        # Process with Claude
        logger.info(f"Processing comparison request with Claude...")
        settings.system_config.llm.provider = LLMProvider.CLAUDE
        claude_start = datetime.now()
        claude_response = await self.process_request(request_text, user_id)
        claude_duration = (datetime.now() - claude_start).total_seconds()
        
        claude_output_tokens = cost_service.estimate_tokens(claude_response.response)
        claude_cost = cost_service.calculate_cost(LLMProvider.CLAUDE, input_tokens, claude_output_tokens)
        logger.info(f"Claude - Output tokens: {claude_output_tokens}, Cost: ${claude_cost:.6f}")
        
        # Calculate hallucination score based on confidence and response characteristics
        claude_hallucination = self._calculate_hallucination_score(
            claude_response.confidence,
            len(claude_response.knowledge_sources),
            claude_response.escalation.should_escalate
        )
        
        claude_metrics = ComparisonMetrics(
            provider=LLMProvider.CLAUDE,
            processing_time=claude_duration,
            estimated_cost=claude_cost,
            hallucination_score=claude_hallucination,
            response_quality=claude_response.confidence
        )
        
        # Process with GPT-4o Mini
        logger.info(f"Processing comparison request with GPT-4o Mini...")
        settings.system_config.llm.provider = LLMProvider.GPT4O_MINI
        gpt4o_start = datetime.now()
        gpt4o_response = await self.process_request(request_text, user_id)
        gpt4o_duration = (datetime.now() - gpt4o_start).total_seconds()
        
        gpt4o_output_tokens = cost_service.estimate_tokens(gpt4o_response.response)
        gpt4o_cost = cost_service.calculate_cost(LLMProvider.GPT4O_MINI, input_tokens, gpt4o_output_tokens)
        logger.info(f"GPT-4o Mini - Output tokens: {gpt4o_output_tokens}, Cost: ${gpt4o_cost:.6f}")
        
        # Calculate hallucination score
        gpt4o_hallucination = self._calculate_hallucination_score(
            gpt4o_response.confidence,
            len(gpt4o_response.knowledge_sources),
            gpt4o_response.escalation.should_escalate
        )
        
        gpt4o_metrics = ComparisonMetrics(
            provider=LLMProvider.GPT4O_MINI,
            processing_time=gpt4o_duration,
            estimated_cost=gpt4o_cost,
            hallucination_score=gpt4o_hallucination,
            response_quality=gpt4o_response.confidence
        )
        
        # Process with Gemini
        logger.info(f"Processing comparison request with Gemini...")
        settings.system_config.llm.provider = LLMProvider.GEMINI
        gemini_start = datetime.now()
        gemini_response = await self.process_request(request_text, user_id)
        gemini_duration = (datetime.now() - gemini_start).total_seconds()
        
        gemini_output_tokens = cost_service.estimate_tokens(gemini_response.response)
        gemini_cost = cost_service.calculate_cost(LLMProvider.GEMINI, input_tokens, gemini_output_tokens)
        logger.info(f"Gemini - Output tokens: {gemini_output_tokens}, Cost: ${gemini_cost:.6f}")
        
        # Calculate hallucination score
        gemini_hallucination = self._calculate_hallucination_score(
            gemini_response.confidence,
            len(gemini_response.knowledge_sources),
            gemini_response.escalation.should_escalate
        )
        
        gemini_metrics = ComparisonMetrics(
            provider=LLMProvider.GEMINI,
            processing_time=gemini_duration,
            estimated_cost=gemini_cost,
            hallucination_score=gemini_hallucination,
            response_quality=gemini_response.confidence
        )
        
        # Determine winner based on confidence, tie-break with cost
        responses_with_metrics = [
            (claude_response, claude_cost, LLMProvider.CLAUDE),
            (gpt4o_response, gpt4o_cost, LLMProvider.GPT4O_MINI),
            (gemini_response, gemini_cost, LLMProvider.GEMINI)
        ]
        
        # Sort by confidence (desc), then cost (asc)
        responses_with_metrics.sort(key=lambda x: (-x[0].confidence, x[1]))
        winner = responses_with_metrics[0][2]

        return ComparisonResponse(
            request_id=request_id,
            original_request=request_text,
            claude_metrics=claude_metrics,
            gpt4o_mini_metrics=gpt4o_metrics,
            gemini_metrics=gemini_metrics,
            claude_response=claude_response,
            gpt4o_mini_response=gpt4o_response,
            gemini_response=gemini_response,
            winner=winner
        )

    def refresh_knowledge_base(self) -> bool:
        """
        Refresh the knowledge base with updated documents.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Refreshing knowledge base...")
            
            # Reset vector store
            success = self.vector_store.reset_collection()
            if not success:
                logger.error("Failed to reset vector store collection")
                return False
            
            # Reload documents
            self._initialize_knowledge_base_sync()
            
            logger.info("Knowledge base refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing knowledge base: {str(e)}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status and metrics.
        
        Returns:
            Dictionary with system status information
        """
        try:
            # Get vector store stats
            vector_stats = self.vector_store.get_collection_stats()
            
            # Get workflow metrics
            workflow_metrics = self.workflow.get_workflow_metrics()
            
            return {
                "initialized": self.is_initialized,
                "timestamp": datetime.now().isoformat(),
                "knowledge_base": vector_stats,
                "workflow_metrics": workflow_metrics,
                "configuration": {
                    "claude_model": settings.system_config.llm.claude_model,
                    "gpt4o_mini_model": settings.system_config.llm.gpt4o_mini_model,
                    "gemini_model": settings.system_config.llm.gemini_model,
                    "temperature": settings.system_config.llm.temperature,
                    "escalation_threshold": settings.system_config.escalation_threshold,
                    "min_confidence_threshold": settings.system_config.min_confidence_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                "initialized": self.is_initialized,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def create_sample_requests() -> List[Dict[str, str]]:
    """Create sample requests for testing."""
    return [
        {
            "request": "I forgot my password and can't log into my computer. How do I reset it?",
            "user_id": "user001"
        },
        {
            "request": "I need to install Microsoft Office on my new laptop. Can you help?",
            "user_id": "user002"
        },
        {
            "request": "My internet connection is not working. I can't access any websites.",
            "user_id": "user003"
        },
        {
            "request": "I think I received a phishing email. It looks suspicious and asks for my login details.",
            "user_id": "user004"
        },
        {
            "request": "My printer is not working. It shows an error message but I can't read it clearly.",
            "user_id": "user005"
        }
    ]


def main():
    """Main function to demonstrate the help desk system."""
    # Initialize system
    system = HelpDeskSystem()
    
    print("=== AI Help Desk System ===")
    print("Initializing system...")
    
    if not system.initialize_sync():
        print("Failed to initialize system. Check logs for details.")
        return
    
    print("System initialized successfully!")
    
    # Get system status
    status = system.get_system_status()
    print(f"\nKnowledge Base: {status['knowledge_base']['document_count']} documents loaded")
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter help desk requests (type 'quit' to exit):")
    
    while True:
        try:
            request_text = input("\nYour request: ").strip()
            
            if request_text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not request_text:
                continue
            
            response = system.process_request_sync(request_text)
            
            print(f"\nCategory: {response.category.value}")
            print(f"Confidence: {response.confidence:.2f}")
            print(f"\nResponse:\n{response.response}")
            
            if response.escalation.should_escalate:
                print(f"\n⚠️  This request will be escalated to: {response.escalation.suggested_department}")
                print(f"Priority: {response.escalation.priority.value}")
                print(f"Reason: {response.escalation.reasoning}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nThank you for using the AI Help Desk System!")


if __name__ == "__main__":
    main()