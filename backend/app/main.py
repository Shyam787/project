from fastapi import HTTPException
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.v1.health import router as health_router
from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.core.config import Settings, get_settings
from app.core.errors import error_response, http_exception_handler, validation_exception_handler
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.core.metrics import MetricsMiddleware
from app.db.bootstrap import create_schema
from app.db.session import create_engine, create_session_factory
from app.documents.router import router as documents_router
from app.platform.router import router as platform_router
from app.retrieval.qdrant_store import QdrantVectorStore


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    logger = get_logger(__name__)

    app = FastAPI(
        title=resolved_settings.app_name,
        version="0.1.0",
        docs_url="/docs" if resolved_settings.enable_docs else None,
        redoc_url="/redoc" if resolved_settings.enable_docs else None,
    )
    app.state.settings = resolved_settings
    app.state.engine = create_engine(resolved_settings)
    app.state.session_factory = create_session_factory(app.state.engine)
    app.state.vector_store = QdrantVectorStore(resolved_settings.qdrant_url)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3002"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(health_router, prefix=resolved_settings.api_v1_prefix)
    app.include_router(auth_router, prefix=resolved_settings.api_v1_prefix)
    app.include_router(documents_router, prefix=resolved_settings.api_v1_prefix)
    app.include_router(chat_router, prefix=resolved_settings.api_v1_prefix)
    app.include_router(platform_router, prefix=resolved_settings.api_v1_prefix)
    app.include_router(health_router)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    @app.on_event("startup")
    async def startup() -> None:
        if resolved_settings.local_auto_migrate:
            await create_schema(app.state.engine)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await app.state.engine.dispose()

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            "unhandled_exception",
            request_id=request_id,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "payload": None,
                "metadata": {"request_id": request_id},
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal error occurred.",
                },
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return error_response(
            request=request,
            status_code=400,
            code="VALIDATION_ERROR",
            message=str(exc),
        )

    logger.info("application_started", environment=resolved_settings.app_env)
    return app
