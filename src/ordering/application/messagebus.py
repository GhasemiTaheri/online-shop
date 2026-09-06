"""Application message dispatch."""

from collections.abc import Awaitable, Callable
import logging
from typing import Any

from ordering.domain.commands import Command

logger = logging.getLogger(__name__)


class MessageBus:
    """Invoke the handler registered for an application command."""

    def __init__(
        self,
        command_handlers: dict[type[Command], Callable[[Command], Awaitable[Any]]],
    ) -> None:
        self._command_handlers = command_handlers

    async def handle(self, message: Command) -> Any:
        """Invoke the registered command handler."""

        try:
            handler = self._command_handlers[type(message)]
        except KeyError as exc:
            raise ValueError(
                f"No command handler is registered for {type(message).__name__}."
            ) from exc

        return await handler(message)
