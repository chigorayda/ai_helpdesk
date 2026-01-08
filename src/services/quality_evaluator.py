"""
Quality evaluation service using LLM-as-judge for response quality assessment.
"""
import logging
from typing import Optional
from src.models.schemas import LLMProvider
from src.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class QualityEvaluator:
    """
    LLM-as-judge service for evaluating response quality.
    Uses a lightweight model (Llama 3.1 8B) for fast, cost-effective evaluation.
    """
    
    def __init__(self):
        """Initialize the quality evaluator."""
        self.llm_service = llm_service
        # Use lightweight model for evaluation
        self.judge_provider = LLMProvider.LLAMA_31_8B
        
    def evaluate_response_quality(
        self,
        original_request: str,
        response_text: str,
        has_knowledge_sources: bool = False,
        knowledge_sources_count: int = 0
    ) -> float:
        """
        Evaluate the quality of a help desk response.
        
        Args:
            original_request: The original user request
            response_text: The generated response to evaluate
            has_knowledge_sources: Whether knowledge base sources were used
            knowledge_sources_count: Number of knowledge sources used
            
        Returns:
            Quality score from 0.0 to 1.0 (higher is better)
        """
        try:
            evaluation_prompt = self._build_evaluation_prompt(
                original_request,
                response_text,
                has_knowledge_sources,
                knowledge_sources_count
            )
            
            # Get evaluation from judge LLM
            judge_response = self.llm_service.generate_response_sync(
                prompt=evaluation_prompt,
                temperature=0.1,  # Low temperature for consistent scoring
                provider=self.judge_provider
            )
            
            # Parse score from response
            score = self._parse_score(judge_response)
            
            logger.debug(f"Quality evaluation: {score:.2f} for response length {len(response_text)}")
            return score
            
        except Exception as e:
            logger.error(f"Error evaluating response quality: {str(e)}")
            # Return neutral score on error
            return 0.5
    
    def _build_evaluation_prompt(
        self,
        request: str,
        response: str,
        has_knowledge: bool,
        knowledge_count: int
    ) -> str:
        """Build the evaluation prompt for the judge LLM."""
        
        knowledge_context = ""
        if has_knowledge:
            knowledge_context = f"\n- Used {knowledge_count} knowledge base sources"
        
        prompt = f"""You are an expert IT support quality assessor. Evaluate the following help desk response.

USER REQUEST:
{request}

HELP DESK RESPONSE:
{response}

CONTEXT:{knowledge_context}

Evaluate this response on these criteria:
1. **Completeness** (0-3): Does it fully address the user's question?
2. **Clarity** (0-3): Is it clear, well-structured, and easy to understand?
3. **Actionability** (0-2): Does it provide specific, actionable steps?
4. **Professionalism** (0-2): Is the tone appropriate and helpful?

Scoring:
- Completeness: 0=Missing key info, 1=Partial, 2=Good, 3=Complete
- Clarity: 0=Confusing, 1=Unclear, 2=Clear, 3=Very clear
- Actionability: 0=Vague, 1=Some steps, 2=Clear actions
- Professionalism: 0=Poor, 1=Acceptable, 2=Professional

IMPORTANT: Respond with ONLY a JSON object, nothing else:
{{"completeness": X, "clarity": X, "actionability": X, "professionalism": X, "total": Y}}

Where total = completeness + clarity + actionability + professionalism (max 10)"""

        return prompt
    
    def _parse_score(self, judge_response: str) -> float:
        """
        Parse the score from judge LLM response.
        
        Args:
            judge_response: Raw response from judge LLM
            
        Returns:
            Normalized score from 0.0 to 1.0
        """
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', judge_response)
            if not json_match:
                logger.warning(f"No JSON found in judge response: {judge_response[:100]}")
                return 0.5
            
            json_str = json_match.group(0)
            scores = json.loads(json_str)
            
            # Get total score (max 10)
            total = scores.get('total', 0)
            
            # Normalize to 0.0-1.0
            normalized_score = min(max(total / 10.0, 0.0), 1.0)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error parsing judge score: {str(e)}")
            # Try to extract number directly
            try:
                numbers = re.findall(r'\d+', judge_response)
                if numbers:
                    total = int(numbers[-1])  # Assume last number is total
                    return min(max(total / 10.0, 0.0), 1.0)
            except:
                pass
            
            return 0.5


# Global instance
quality_evaluator = QualityEvaluator()
