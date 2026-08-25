"""Transaction boundary abstractions for the Ordering application layer."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from ordering.application.repository import IdempotencyRepositoryAbs, OrderRepositoryAbs


class OrderingUowAbs(ABC):
    """Defines the local transaction boundary for Ordering use cases."""

    orders: OrderRepositoryAbs
    idempotency: IdempotencyRepositoryAbs

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Start the transaction and return this unit of work."""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Finish the transaction scope and release its resources."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current local transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Abort the current local transaction."""
