"""
Service for calculating estimated costs of LLM API calls.
"""
from src.models.schemas import LLMProvider

class CostService:
    """Service to calculate LLM costs."""
    
    # Prices per 1M tokens via OpenRouter (as of Dec 16, 2024)
    # OpenRouter pricing: https://openrouter.ai/models
    # Note: Prices are per 1M tokens, converted to per 1k tokens below
    PRICES = {
        LLMProvider.CLAUDE: {
            "input": 0.003,     # Claude 3.5 Sonnet: $3.00/1M tokens = $0.003/1k
            "output": 0.015     # Claude 3.5 Sonnet: $15.00/1M tokens = $0.015/1k
        },
        LLMProvider.GPT4O_MINI: {
            "input": 0.00015,   # GPT-4o Mini: $0.15/1M tokens = $0.00015/1k
            "output": 0.0006    # GPT-4o Mini: $0.60/1M tokens = $0.0006/1k
        },
        LLMProvider.GEMINI: {
            "input": 0.0003,       # Gemini 2.0 Flash: $0.30/1M tokens
            "output": 0.00125       # Gemini 2.0 Flash: $1.25/1M tokens
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
            print(f"Warning: No pricing info for {provider}, returning 0.0")
            return 0.0
            
        pricing = self.PRICES[provider]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        print(f"Cost calculation for {provider.value}: Input={input_tokens} tokens (${input_cost:.6f}), Output={output_tokens} tokens (${output_cost:.6f}), Total=${total_cost:.6f}")
        
        return total_cost

    def estimate_tokens(self, text: str) -> int:
        """
        Roughly estimate token count (approx 4 chars per token).
        For accurate counting, tiktoken or similar libraries should be used.
        """
        return len(text) // 4

cost_service = CostService()