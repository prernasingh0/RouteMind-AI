from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config.logging import configure_logging
from app.config.settings import get_settings
from app.infrastructure.cache.redis import close_redis
from app.middleware.errors import ErrorHandlingMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

def custom_openapi():
    if app.openapi_schema: return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(title=settings.PROJECT_NAME, version="0.2.0", description="Enterprise backend API for RouteMind AI.", routes=app.routes)
    schema["servers"] = [{"url": settings.API_V1_PREFIX, "description": "Version 1 API"}]
    app.openapi_schema = schema
    return app.openapi_schema

app = FastAPI(title=settings.PROJECT_NAME, version="0.2.0", docs_url="/docs", redoc_url="/redoc")
app.openapi = custom_openapi
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.on_event("shutdown")
async def shutdown() -> None:
    await close_redis()
