"""Idempotency records and errors for Ordering commands."""

from dataclasses import dataclass
from datetime import datetime

from ordering.domain.order import CustomerId, OrderId
from ordering.exceptions import ConflictException


ORDER_CREATE_ROUTE = "POST:/api/v1/orders"


class IdempotencyConflictError(ConflictException):
    """Raised when a key is replayed with a different request payload."""


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """The durable result of an idempotent command within its active window."""

    customer_id: CustomerId
    route: str
    key: str
    request_fingerprint: str
    order_id: OrderId
    expires_at: datetime
    active: bool = True
