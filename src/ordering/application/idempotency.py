"""Application idempotency constants and errors for Ordering commands."""

from ordering.exceptions import ConflictException


ORDER_CREATE_ROUTE = "POST:/api/v1/orders"


class IdempotencyConflictError(ConflictException):
    """Raised when a key is replayed with a different request payload."""


class IdempotencyKeyAlreadyExistsError(Exception):
    """An active idempotency key was inserted concurrently.

    This internal signal lets the use case retry only the expected race on the
    partial unique idempotency index, rather than retrying arbitrary database
    uniqueness failures.
    """
