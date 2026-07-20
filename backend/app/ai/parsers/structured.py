from collections.abc import Awaitable, Callable
from pydantic import BaseModel, ValidationError

class StructuredOutputValidator:
    def __init__(self, max_attempts: int = 3): self.max_attempts=max_attempts
    async def validate_with_retry(self, producer: Callable[[], Awaitable[BaseModel]]) -> BaseModel:
        last_error: Exception | None = None
        for _ in range(self.max_attempts):
            try: return await producer()
            except (ValidationError, ValueError) as exc: last_error = exc
        if last_error: raise last_error
        raise ValueError("Structured output validation failed")
