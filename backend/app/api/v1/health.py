from fastapi import APIRouter, Request

from app.core.pipeline import GOVERNED_PIPELINE_ORDER

router = APIRouter(tags=["operations"])


@router.get("/health")
async def health(request: Request) -> dict:
    return {
        "success": True,
        "payload": {"status": "ok"},
        "metadata": {
            "request_id": getattr(request.state, "request_id", "unknown"),
            "service": request.app.state.settings.app_name,
        },
        "error": None,
    }


@router.get("/ready")
async def ready(request: Request) -> dict:
    settings = request.app.state.settings
    return {
        "success": True,
        "payload": {
            "status": "ready",
            "environment": settings.app_env,
            "pipeline_order": GOVERNED_PIPELINE_ORDER,
        },
        "metadata": {
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
        "error": None,
    }
