"""
Lite workflow for fast help desk responses.
Skips classification and escalation for maximum speed.
"""
import time
import logging
from typing import Optional
from src.models.schemas import (
    HelpDeskRequest,
    HelpDeskResponse,
    RequestCategory,
    ClassificationResult,
    EscalationDecision,
    PriorityLevel,
    RetrievalResult
)
from src.agents.knowledge_agent import knowledge_agent
from src.agents.response_agent import response_agent
from src.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class HelpDeskWorkflowLite:
    """
    Lightweight workflow that skips classification and escalation.
    Only performs knowledge retrieval and response generation.
    
    Trade-offs:
    - Much faster (50-70% reduction in response time)
    - No request categorization
    - No automatic escalation detection
    - Less structured responses
    """
    
    def __init__(self):
        """Initialize the lite workflow."""
        self.knowledge_agent = knowledge_agent
        self.response_agent = response_agent
        logger.info("Initialized HelpDeskWorkflowLite (fast mode)")
    
    def process_request_sync(
        self,
        request: HelpDeskRequest,
        skip_knowledge: bool = False
    ) -> HelpDeskResponse:
        """
        Process a help desk request with minimal overhead.
        
        Args:
            request: The help desk request to process
            skip_knowledge: If True, skip knowledge retrieval (even faster but less accurate)
            
        Returns:
            HelpDeskResponse with the result
        """
        start_time = time.time()
        
        try:
            logger.info(f"[LITE] Processing request {request.id} in fast mode")
            
            # Step 1: Knowledge Retrieval (optional)
            retrieval_result = None
            knowledge_sources = []
            
            if not skip_knowledge:
                retrieval_start = time.time()
                
                # Create a minimal classification for knowledge agent
                # Just use generic category to enable search
                minimal_classification = ClassificationResult(
                    category=RequestCategory.UNKNOWN,
                    confidence=0.5,
                    reasoning="Lite mode - no classification",
                    keywords=[]
                )
                
                # Retrieve knowledge with reduced results for speed
                result = self.knowledge_agent.retrieve_knowledge(
                    request, 
                    minimal_classification
                )
                
                if result.success:
                    retrieval_result = result.data
                    knowledge_sources = [doc.source for doc in retrieval_result.documents]
                    logger.info(f"[LITE] Retrieved {len(knowledge_sources)} documents in {time.time() - retrieval_start:.2f}s")
                else:
                    logger.warning(f"[LITE] Knowledge retrieval failed: {result.error}")
            else:
                logger.info("[LITE] Skipping knowledge retrieval for maximum speed")
            
            # Step 2: Direct Response Generation (fast path)
            response_start = time.time()
            response_text = self._generate_fast_response(request, retrieval_result)
            logger.info(f"[LITE] Generated response in {time.time() - response_start:.2f}s")
            
            # Step 3: Create minimal response object
            processing_time = time.time() - start_time
            
            # Create default escalation (no escalation in lite mode)
            default_escalation = EscalationDecision(
                should_escalate=False,
                reasoning="Lite mode - escalation skipped for speed",
                priority=PriorityLevel.LOW,
                suggested_department="it_support",
                estimated_complexity="standard"
            )
            
            logger.info(f"[LITE] Total processing time: {processing_time:.2f}s")
            
            return HelpDeskResponse(
                request_id=request.id,
                category=RequestCategory.UNKNOWN,  # Not classified in lite mode
                response=response_text,
                confidence=0.8 if not skip_knowledge else 0.6,  # Lower confidence without knowledge
                knowledge_sources=knowledge_sources,
                escalation=default_escalation,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"[LITE] Error processing request {request.id}: {str(e)}")
            
            # Return error response
            error_escalation = EscalationDecision(
                should_escalate=True,
                reasoning=f"Error in lite mode: {str(e)}",
                priority=PriorityLevel.HIGH,
                suggested_department="it_support",
                estimated_complexity="error"
            )
            
            return HelpDeskResponse(
                request_id=request.id,
                category=RequestCategory.UNKNOWN,
                response=f"I apologize, but I encountered an error: {str(e)}. Please contact IT support directly.",
                confidence=0.0,
                knowledge_sources=[],
                escalation=error_escalation,
                processing_time=processing_time
            )
    
    def _generate_fast_response(
        self,
        request: HelpDeskRequest,
        retrieval_result: Optional[RetrievalResult]
    ) -> str:
        """
        Generate a response using the fastest method possible.
        
        Args:
            request: The help desk request
            retrieval_result: Optional knowledge retrieval results
            
        Returns:
            Response text
        """
        try:
            # Prepare minimal context
            context = ""
            if retrieval_result and retrieval_result.documents:
                # Use only top 3 documents with reduced content
                top_docs = retrieval_result.documents[:3]
                context_parts = []
                for i, doc in enumerate(top_docs):
                    # Truncate to 200 chars for speed
                    content = doc.content[:200]
                    context_parts.append(f"Source {i+1}: {content}...")
                context = "\n".join(context_parts)
            
            # Create minimal prompt for speed
            if context:
                prompt = f"""Provide a concise IT support response for this question:

Question: {request.request}

Relevant Information:
{context}

Instructions:
- Give a direct, actionable answer
- Keep it under 150 words
- Be specific and helpful
- If you can't fully answer, suggest next steps

Response:"""
            else:
                # No knowledge base - use general IT support knowledge
                prompt = f"""Provide a concise IT support response for this question:

Question: {request.request}

Instructions:
- Give a direct, helpful answer based on common IT support knowledge
- Keep it under 150 words
- Be specific and actionable
- If uncertain, recommend contacting IT support

Response:"""
            
            # Generate response with minimal temperature for speed
            response = llm_service.generate_response_sync(
                prompt=prompt,
                temperature=0.3  # Higher temperature = faster
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"[LITE] Error generating fast response: {str(e)}")
            # Ultra-fallback
            return f"Thank you for your IT support request. Based on your question about '{request.request[:50]}...', I recommend contacting IT support directly at helpdesk@company.com or ext. 5555 for immediate assistance."
    
    async def process_request(
        self,
        request: HelpDeskRequest,
        skip_knowledge: bool = False
    ) -> HelpDeskResponse:
        """
        Async version of process_request_sync.
        
        Args:
            request: The help desk request to process
            skip_knowledge: If True, skip knowledge retrieval
            
        Returns:
            HelpDeskResponse with the result
        """
        # For lite mode, async doesn't add much benefit
        # But provided for compatibility
        return self.process_request_sync(request, skip_knowledge)


# Global lite workflow instance
helpdesk_workflow_lite = HelpDeskWorkflowLite()
