"""Inbound Catalog snapshot port owned by Ordering."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProductSnapshot:
    product_id: UUID
    name: str
    unit_price: Decimal
    currency: str
    active: bool


class ProductSnapshotProvider(Protocol):
    async def get_many(self, product_ids: tuple[UUID, ...]) -> dict[UUID, ProductSnapshot]: ...
