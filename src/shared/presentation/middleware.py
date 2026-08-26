"""HTTP middleware shared by API routers."""

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

from shared.observability.context import (
    reset_observability_context,
    set_observability_context,
)

logger = logging.getLogger(__name__)


def install_correlation_middleware(app: FastAPI) -> None:
    """Create request correlation context and log one completion record per request."""

    @app.middleware("http")
    async def correlate_request(request: Request, call_next):
        request_correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        tokens = set_observability_context(correlation=request_correlation_id)
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "api.request_failed",
                extra={
                    "context": "api",
                    "operation": "http_request",
                    "status_code": 500,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                },
            )
            raise
        else:
            response.headers["X-Correlation-ID"] = request_correlation_id
            status_code = response.status_code
            level = logging.INFO if status_code < 400 else logging.WARNING
            logger.log(
                level,
                "api.request_completed",
                extra={
                    "context": "api",
                    "operation": "http_request",
                    "status_code": status_code,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                },
            )
            return response
        finally:
            reset_observability_context(tokens)
