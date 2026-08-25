"""Application message dispatch with a unit-of-work scope."""

from collections.abc import Awaitable, Callable
import logging
from typing import Any

from pymongo.errors import DuplicateKeyError
from ordering.application.uow import OrderingUowAbs
from ordering.domain.commands import Command

logger = logging.getLogger(__name__)


class MessageBus:
    """Dispatch application commands to their registered handlers."""

    def __init__(
            self,
            uow: OrderingUowAbs,
            command_handlers: dict[type[Command], Callable[[Command], Awaitable[Any]]],
    ) -> None:
        self._uow = uow
        self._command_handlers = command_handlers

    async def handle(self, message: Command) -> Any:
        """Run a command handler within a transaction scope."""

        try:
            handler = self._command_handlers[type(message)]
        except KeyError as exc:
            raise ValueError(
                f"No command handler is registered for {type(message).__name__}."
            ) from exc

        for attempt in range(2):
            try:
                async with self._uow:
                    return await handler(message)
            except DuplicateKeyError:
                logger.warning(
                    "ordering.command_duplicate_key_retry",
                    extra={
                        "context": "ordering",
                        "operation": type(message).__name__,
                        "attempt": attempt + 1,
                    },
                )
                if attempt == 1:
                    raise

        raise AssertionError("The duplicate-key retry loop must return or raise.")
