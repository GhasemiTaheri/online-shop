"""Product aggregate owned by Catalog."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import NewType
from uuid import UUID


ProductId = NewType("ProductId", UUID)


class Currency(StrEnum):
    EUR = "EUR"


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: Currency


class Product:
    def __init__(self, id: ProductId, sku: str, name: str, description: str | None,
                 price: Money, active: bool, version: int, created_at: datetime,
                 updated_at: datetime) -> None:
        if not name.strip():
            raise ValueError("Product name must not be empty.")
        if price.amount < 0 or price.currency is not Currency.EUR:
            raise ValueError("Products require a non-negative EUR price.")
        self.id, self.sku, self.name, self.description = id, sku, name, description
        self.price, self.active, self.version = price, active, version
        self.created_at, self.updated_at = created_at, updated_at

    def change_price(self, price: Money, updated_at: datetime) -> None:
        if price.amount < 0 or price.currency is not Currency.EUR:
            raise ValueError("Products require a non-negative EUR price.")
        self.price = price
        self.version += 1
        self.updated_at = updated_at
