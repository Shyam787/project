from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict | list | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "payload": None,
            "metadata": {
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
        },
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = detail.get("code", "HTTP_ERROR")
    message = detail.get("message", str(exc.detail))
    return error_response(
        request=request,
        status_code=exc.status_code,
        code=code,
        message=message,
        details=detail.get("details"),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return error_response(
        request=request,
        status_code=400,
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        details=exc.errors(),
    )
