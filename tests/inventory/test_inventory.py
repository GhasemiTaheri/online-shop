from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from inventory.application.reserve_inventory import reserve_inventory
from inventory.domain.inventory import InventoryItem, ProductId, ReservationStatus
from inventory.domain.repository import InventoryItemRepositoryAbs, ReservationRepositoryAbs


class Items(InventoryItemRepositoryAbs):
    def __init__(self, values): self.values = values
    async def get_many(self, product_ids): return {key: self.values[key] for key in product_ids if key in self.values}
    async def save(self, item, expected_version):
        if item.version - 1 != expected_version: raise RuntimeError("version conflict")


class Reservations(ReservationRepositoryAbs):
    def __init__(self): self.value = None
    async def get_by_order(self, order_id): return self.value if self.value and self.value.order_id == order_id else None
    async def add(self, reservation): self.value = reservation


@pytest.mark.asyncio
async def test_reservation_is_deterministic_and_expires_after_24_hours() -> None:
    first, second = uuid4(), uuid4()
    items = Items({ProductId(first): InventoryItem(ProductId(first), 5), ProductId(second): InventoryItem(ProductId(second), 3)})
    reservations = Reservations()
    now = datetime.now(UTC)
    result = await reserve_inventory(uuid4(), ((second, 1), (first, 2)), items, reservations, now)
    assert [line.product_id for line in result.items] == [ProductId(min(first, second)), ProductId(max(first, second))]
    assert result.expires_at == now + timedelta(hours=24)
    result.expire(result.expires_at)
    assert result.status is ReservationStatus.EXPIRED


def test_adjustment_cannot_reduce_below_reserved() -> None:
    item = InventoryItem(ProductId(uuid4()), 5, reserved=3)
    with pytest.raises(ValueError): item.adjust(-3)
