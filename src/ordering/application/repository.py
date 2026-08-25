"""Repository interfaces owned by the Ordering application layer."""

from abc import ABC, abstractmethod

from ordering.domain.order import Order, OrderId


class OrderRepositoryAbs(ABC):
    """Persistence operations required by Ordering use cases."""

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Persist a new order in the active unit-of-work transaction."""

    @abstractmethod
    async def get(self, order_id: OrderId) -> Order | None:
        """Return an order by ID, or ``None`` when it does not exist."""
