"""Domain models owned by the Ordering bounded context."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import NewType
from uuid import UUID


OrderId = NewType("OrderId", UUID)
CustomerId = NewType("CustomerId", UUID)
ProductId = NewType("ProductId", UUID)


class Currency(StrEnum):
    """Currencies supported by the Ordering context."""

    EUR = "EUR"


class OrderStatus(StrEnum):
    """Persisted stages of an order's fulfillment lifecycle."""

    PENDING = "PENDING"
    AWAITING_INVENTORY = "AWAITING_INVENTORY"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    FULFILLING = "FULFILLING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    REJECTED = "REJECTED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in the currency recorded at order placement."""

    amount: Decimal
    currency: Currency


@dataclass(frozen=True, slots=True)
class ShippingAddress:
    """An immutable delivery-address snapshot owned by an order."""

    recipient_name: str
    line_1: str
    line_2: str | None
    city: str
    postal_code: str
    country_code: str


@dataclass(frozen=True, slots=True)
class OrderItem:
    """An immutable product and price snapshot within an order."""

    product_id: ProductId
    product_name: str
    unit_price: Money
    quantity: int
    subtotal: Money


class Order:
    """The Ordering aggregate root."""

    def __init__(
        self,
        id: OrderId,
        customer_id: CustomerId,
        items: tuple[OrderItem, ...],
        shipping_address: ShippingAddress,
        total: Money,
        status: OrderStatus,
        version: int,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.id = id
        self.customer_id = customer_id
        self.items = items
        self.shipping_address = shipping_address
        self.total = total
        self.status = status
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
