"""Exceptions owned by the Ordering bounded context.

They express failures in Ordering terms and deliberately do not depend on
FastAPI. Ordering routes translate them into HTTP responses.
"""


class OrderingException(Exception):
    """Base class for expected Ordering failures."""

    code = "ORDERING_ERROR"
    status_code = 500
    expose_message = False


class ApplicationException(OrderingException):
    """An Ordering use case cannot complete because of an internal condition."""

    code = "ORDERING_APPLICATION_ERROR"


class DomainException(OrderingException):
    """A violated Ordering business rule or domain invariant."""

    code = "ORDERING_DOMAIN_ERROR"
    status_code = 422
    expose_message = True


class NotFoundException(DomainException):
    """An Ordering resource requested by the use case does not exist."""

    code = "ORDER_NOT_FOUND"
    status_code = 404


class ConflictException(DomainException):
    """An Ordering operation conflicts with the current state."""

    code = "ORDERING_CONFLICT"
    status_code = 409


class InfraException(OrderingException):
    """An Ordering dependency cannot complete the requested operation."""

    code = "ORDERING_INFRASTRUCTURE_UNAVAILABLE"
    status_code = 503


class InvalidCursorError(OrderingException):
    code = "ORDERING_INVALID_CURSOR"
    status_code = 400
    expose_message = True
