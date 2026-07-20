from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
logger = structlog.get_logger()
class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception("unhandled_error", path=request.url.path, error=str(exc))
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":"Internal server error"})
