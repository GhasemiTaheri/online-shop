"""Transport-independent commands for the Ordering context."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Command(BaseModel):
    """Base type for messages dispatched by the application message bus."""

    model_config = ConfigDict(frozen=True)


class CreateOrderItem(Command):
    """A requested product line."""

    product_id: UUID
    quantity: int = Field(gt=0)


class CreateOrderShippingAddress(Command):
    """The delivery address captured when the order is placed."""

    recipient_name: str = Field(min_length=1)
    line_1: str = Field(min_length=1)
    line_2: str | None = None
    city: str = Field(min_length=1)
    postal_code: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)


class CreateOrder(Command):
    """All input required to create an order, independent of HTTP."""

    customer_id: UUID
    items: tuple[CreateOrderItem, ...] = Field(min_length=1)
    shipping_address: CreateOrderShippingAddress
    payment_method: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
