"""Request and message correlation context for logs and integration events."""

from contextvars import ContextVar, Token


correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
causation_id: ContextVar[str | None] = ContextVar("causation_id", default=None)


def set_observability_context(
    *, correlation: str, causation: str | None = None
) -> tuple[Token[str | None], Token[str | None]]:
    """Bind workflow identifiers to the current async execution context."""

    return correlation_id.set(correlation), causation_id.set(causation)


def reset_observability_context(tokens: tuple[Token[str | None], Token[str | None]]) -> None:
    """Restore the context that was active before a request or message."""

    correlation_id.reset(tokens[0])
    causation_id.reset(tokens[1])
