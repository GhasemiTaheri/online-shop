import json
import logging

from shared.observability.context import (
    reset_observability_context,
    set_observability_context,
)
from shared.observability.logging import JsonFormatter


def test_json_formatter_includes_context_and_only_allowlisted_fields() -> None:
    tokens = set_observability_context(correlation="workflow-123", causation="event-456")
    try:
        record = logging.makeLogRecord(
            {
                "name": "ordering.application.create_order",
                "levelno": logging.INFO,
                "levelname": "INFO",
                "msg": "ordering.order_created",
                "args": (),
                "aggregate_id": "order-1",
                "payment_token": "must-not-be-emitted",
            }
        )
        payload = json.loads(JsonFormatter().format(record))
    finally:
        reset_observability_context(tokens)

    assert payload["correlation_id"] == "workflow-123"
    assert payload["causation_id"] == "event-456"
    assert payload["aggregate_id"] == "order-1"
    assert "payment_token" not in payload
