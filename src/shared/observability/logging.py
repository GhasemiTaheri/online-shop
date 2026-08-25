"""Structured JSON logging configuration for application processes."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from shared.observability.context import causation_id, correlation_id

LOG_FIELDS = (
    "context",
    "operation",
    "aggregate_type",
    "aggregate_id",
    "event_id",
    "event_type",
    "attempt",
    "duration_ms",
    "status_code",
    "error_code",
)


class JsonFormatter(logging.Formatter):
    """Format allowlisted log fields as one JSON document per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id.get(),
            "causation_id": causation_id.get(),
        }
        for field in LOG_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(level: str) -> None:
    """Configure stdout JSON logging for this API or worker process."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level.upper())

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
