import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar
T = TypeVar("T")
async def with_exponential_backoff(operation: Callable[[], Awaitable[T]], attempts: int = 3, base_delay: float = 0.2) -> T:
    last: Exception | None = None
    for attempt in range(attempts):
        try: return await operation()
        except Exception as exc:
            last = exc
            if attempt < attempts - 1: await asyncio.sleep(base_delay * (2 ** attempt))
    raise last or RuntimeError("operation failed")
