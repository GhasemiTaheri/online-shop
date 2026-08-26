"""Repository contracts owned by the Ordering domain."""

from abc import ABC, abstractmethod
from datetime import datetime

from ordering.domain.idempotency import IdempotencyRecord
from ordering.domain.order import CustomerId, Order, OrderId


class OrderRepositoryAbs(ABC):
    """Persistence operations required by the Order aggregate."""

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Persist a new order in the active unit-of-work transaction."""

    @abstractmethod
    async def get(self, order_id: OrderId) -> Order | None:
        """Return an order by ID, or ``None`` when it does not exist."""


class IdempotencyRepositoryAbs(ABC):
    """Durable idempotency state owned by the Ordering context."""

    @abstractmethod
    async def deactivate_expired(
        self, customer_id: CustomerId, route: str, key: str, now: datetime
    ) -> None:
        """Mark expired records inactive while retaining their audit history."""

    @abstractmethod
    async def get_active(
        self, customer_id: CustomerId, route: str, key: str, now: datetime
    ) -> IdempotencyRecord | None:
        """Return the current active record for a scoped idempotency key."""

    @abstractmethod
    async def add(self, record: IdempotencyRecord) -> None:
        """Persist a new active idempotency record."""
