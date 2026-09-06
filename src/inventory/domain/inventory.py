"""Inventory aggregates and reservation state."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import NewType
from uuid import UUID

ProductId = NewType("ProductId", UUID)
OrderId = NewType("OrderId", UUID)
ReservationId = NewType("ReservationId", UUID)


class ReservationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"


class InventoryItem:
    def __init__(self, product_id: ProductId, on_hand: int, reserved: int = 0, version: int = 1) -> None:
        if on_hand < 0 or reserved < 0 or reserved > on_hand:
            raise ValueError("Inventory quantities are invalid.")
        self.product_id, self.on_hand, self.reserved, self.version = product_id, on_hand, reserved, version

    @property
    def available(self) -> int:
        return self.on_hand - self.reserved

    def adjust(self, amount: int) -> None:
        if self.on_hand + amount < self.reserved:
            raise ValueError("Adjustment cannot reduce stock below reserved quantity.")
        self.on_hand += amount
        self.version += 1

    def reserve(self, quantity: int) -> None:
        if quantity <= 0 or quantity > self.available:
            raise ValueError("Insufficient inventory.")
        self.reserved += quantity
        self.version += 1

    def release(self, quantity: int) -> None:
        if quantity < 0 or quantity > self.reserved:
            raise ValueError("Invalid inventory release.")
        self.reserved -= quantity
        self.version += 1


@dataclass(frozen=True, slots=True)
class ReservationLine:
    product_id: ProductId
    quantity: int


class Reservation:
    def __init__(self, id: ReservationId, order_id: OrderId, items: tuple[ReservationLine, ...],
                 created_at: datetime, expires_at: datetime, status: ReservationStatus = ReservationStatus.ACTIVE) -> None:
        self.id, self.order_id, self.items = id, order_id, items
        self.created_at, self.expires_at, self.status = created_at, expires_at, status

    def release(self) -> None:
        if self.status is ReservationStatus.ACTIVE:
            self.status = ReservationStatus.RELEASED

    def commit(self) -> None:
        if self.status is ReservationStatus.ACTIVE:
            self.status = ReservationStatus.COMMITTED

    def expire(self, now: datetime) -> None:
        if self.status is ReservationStatus.ACTIVE and now >= self.expires_at:
            self.status = ReservationStatus.EXPIRED
