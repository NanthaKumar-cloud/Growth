import time
from typing import Dict, Any

class TelemetryTracker:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.start_time = 0.0
        self.end_time = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        
        # Pricing rates per 1M tokens (USD) for gemini-2.5-flash
        self.input_rate_per_m = 0.075
        self.output_rate_per_m = 0.30

    def start(self):
        self.start_time = time.time()
        self.end_time = 0.0

    def record_usage(self, prompt_tokens: int, completion_tokens: int):
        self.total_input_tokens += prompt_tokens
        self.total_output_tokens += completion_tokens

    def stop(self) -> float:
        self.end_time = time.time()
        return self.elapsed_time()

    def elapsed_time(self) -> float:
        if self.end_time > 0:
            return round(self.end_time - self.start_time, 2)
        elif self.start_time > 0:
            return round(time.time() - self.start_time, 2)
        return 0.0

    def calculate_cost(self) -> float:
        cost = (self.total_input_tokens / 1_000_000.0) * self.input_rate_per_m + \
               (self.total_output_tokens / 1_000_000.0) * self.output_rate_per_m
        return round(cost, 6)

    def summary(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "elapsed_seconds": self.elapsed_time(),
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": f"${self.calculate_cost():.6f}",
        }
