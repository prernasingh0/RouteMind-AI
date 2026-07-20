import time, uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
logger = structlog.get_logger()
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter(); response = await call_next(request); duration_ms = round((time.perf_counter()-start)*1000, 2)
        response.headers["x-request-id"] = request_id
        logger.info("http_request", request_id=request_id, method=request.method, path=request.url.path, status_code=response.status_code, duration_ms=duration_ms)
        return response
