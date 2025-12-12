"""
Service for calculating estimated costs of LLM API calls.
"""
from src.models.schemas import LLMProvider

class CostService:
    """Service to calculate LLM costs."""
    
    # Prices per 1k tokens (approximate as of early 2024/late 2023)
    # These should be updated regularly or fetched dynamically if possible
    PRICES = {
        LLMProvider.GEMINI: {
            "input": 0.000125,  # Gemini 1.5 Flash input
            "output": 0.000375   # Gemini 1.5 Flash output
        },
        LLMProvider.OPENAI: {
            "input": 0.0005,    # GPT-3.5 Turbo input
            "output": 0.0015    # GPT-3.5 Turbo output
        }
    }

    def calculate_cost(self, provider: LLMProvider, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the estimated cost for a request.
        
        Args:
            provider: The LLM provider used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        if provider not in self.PRICES:
            return 0.0
            
        pricing = self.PRICES[provider]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost

    def estimate_tokens(self, text: str) -> int:
        """
        Roughly estimate token count (approx 4 chars per token).
        For accurate counting, tiktoken or similar libraries should be used.
        """
        return len(text) // 4

cost_service = CostService()