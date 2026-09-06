from abc import ABC, abstractmethod
from uuid import UUID

from inventory.domain.inventory import InventoryItem, Reservation


class InventoryItemRepositoryAbs(ABC):
    @abstractmethod
    async def get_many(self, product_ids: tuple[UUID, ...]) -> dict[UUID, InventoryItem]: ...

    @abstractmethod
    async def save(self, item: InventoryItem, expected_version: int) -> None: ...


class ReservationRepositoryAbs(ABC):
    @abstractmethod
    async def get_by_order(self, order_id: UUID) -> Reservation | None: ...

    @abstractmethod
    async def add(self, reservation: Reservation) -> None: ...
