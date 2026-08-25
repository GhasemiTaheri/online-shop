"""Repository interfaces owned by the Ordering application layer."""

from abc import ABC, abstractmethod

from ordering.domain.order import Order, OrderId
from ordering.application.idempotency import IdempotencyRecord
from ordering.domain.order import CustomerId


class OrderRepositoryAbs(ABC):
    """Persistence operations required by Ordering use cases."""

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Persist a new order in the active unit-of-work transaction."""

    @abstractmethod
    async def get(self, order_id: OrderId) -> Order | None:
        """Return an order by ID, or ``None`` when it does not exist."""


class IdempotencyRepositoryAbs(ABC):
    """Durable idempotency state used by Ordering commands."""

    @abstractmethod
    async def deactivate_expired(
        self, customer_id: CustomerId, route: str, key: str, now
    ) -> None:
        """Mark expired records inactive while retaining their audit history."""

    @abstractmethod
    async def get_active(
        self, customer_id: CustomerId, route: str, key: str, now
    ) -> IdempotencyRecord | None:
        """Return the current active record for a scoped idempotency key."""

    @abstractmethod
    async def add(self, record: IdempotencyRecord) -> None:
        """Persist a new active idempotency record."""
