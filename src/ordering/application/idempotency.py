"""Application idempotency constants and errors for Ordering commands."""

from ordering.exceptions import ConflictException


ORDER_CREATE_ROUTE = "POST:/api/v1/orders"


class IdempotencyConflictError(ConflictException):
    """Raised when a key is replayed with a different request payload."""
