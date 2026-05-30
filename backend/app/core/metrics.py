from time import perf_counter

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "enterprise_rag_api_requests_total",
    "Total API requests.",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "enterprise_rag_api_request_latency_seconds",
    "API request latency in seconds.",
    ["method", "path"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        started_at = perf_counter()
        response = await call_next(request)
        elapsed = perf_counter() - started_at
        path = request.scope.get("route").path if request.scope.get("route") else request.url.path
        REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        REQUEST_COUNT.labels(
            request.method,
            path,
            str(response.status_code),
        ).inc()
        return response
