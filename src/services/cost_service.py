"""
Service for calculating estimated costs of LLM API calls.
"""
from src.models.schemas import LLMProvider

class CostService:
    """Service to calculate LLM costs."""
    
    # Prices per 1M tokens via OpenRouter (as of Dec 2024)
    # OpenRouter pricing: https://openrouter.ai/models
    # Note: Prices are per 1M tokens, converted to per 1k tokens below
    PRICES = {
        LLMProvider.CLAUDE: {
            "input": 0.006,     # Claude 3.5 Sonnet: $6.00/1M tokens = $0.006/1k (updated Dec 2024)
            "output": 0.030     # Claude 3.5 Sonnet: $30.00/1M tokens = $0.030/1k (updated Dec 2024)
        },
        LLMProvider.CLAUDE_SONNET_45: {
            "input": 0.003,     # Claude Sonnet 4.5: $3.00/1M tokens = $0.003/1k (updated Dec 2024)
            "output": 0.015     # Claude Sonnet 4.5: $15.00/1M tokens = $0.015/1k (updated Dec 2024)
        },
        LLMProvider.GPT4O_MINI: {
            "input": 0.00015,   # GPT-4o Mini: $0.15/1M tokens = $0.00015/1k (confirmed Dec 2024)
            "output": 0.0006    # GPT-4o Mini: $0.60/1M tokens = $0.0006/1k (confirmed Dec 2024)
        },
        LLMProvider.GPT_52: {
            "input": 0.00175,   # GPT-5.2: $1.75/1M tokens = $0.00175/1k (updated Dec 2024)
            "output": 0.014     # GPT-5.2: $14.00/1M tokens = $0.014/1k (updated Dec 2024)
        },
        LLMProvider.GEMINI: {
            "input": 0.0001,    # Gemini 2.0 Flash: $0.10/1M tokens = $0.0001/1k (updated Dec 2024)
            "output": 0.0004    # Gemini 2.0 Flash: $0.40/1M tokens = $0.0004/1k (updated Dec 2024)
        },
        LLMProvider.GEMINI_3_PRO: {
            "input": 0.002,     # Gemini 3 Pro Preview: $2.00/1M tokens = $0.002/1k (updated Dec 2024)
            "output": 0.012     # Gemini 3 Pro Preview: $12.00/1M tokens = $0.012/1k (updated Dec 2024)
        },
        LLMProvider.GROK_4_FAST: {
            "input": 0.0002,    # Grok 4 Fast: $0.20/1M tokens = $0.0002/1k (updated Dec 2024)
            "output": 0.0005    # Grok 4 Fast: $0.50/1M tokens = $0.0005/1k (updated Dec 2024)
        },
        LLMProvider.DEEPSEEK_V32: {
            "input": 0.00024,   # DeepSeek V3.2: $0.24/1M tokens = $0.00024/1k (updated Dec 2024)
            "output": 0.00038   # DeepSeek V3.2: $0.38/1M tokens = $0.00038/1k (updated Dec 2024)
        },
        LLMProvider.QWEN3_235B: {
            "input": 0.00018,   # Qwen3 235B: $0.18/1M tokens = $0.00018/1k (updated Dec 2024)
            "output": 0.00054   # Qwen3 235B: $0.54/1M tokens = $0.00054/1k (updated Dec 2024)
        },
        LLMProvider.LLAMA_31_8B: {
            "input": 0.00002,   # Llama 3.1 8B: $0.02/1M tokens = $0.00002/1k (confirmed Dec 2024)
            "output": 0.00003   # Llama 3.1 8B: $0.03/1M tokens = $0.00003/1k (confirmed Dec 2024)
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