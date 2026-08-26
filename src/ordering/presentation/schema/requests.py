"""Request schemas for Ordering HTTP endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field


class OrderItemRequest(BaseModel):
    """One product requested for a new order."""

    product_id: UUID
    quantity: int = Field(gt=0)


class ShippingAddressRequest(BaseModel):
    """Delivery address supplied when placing an order."""

    recipient_name: str = Field(min_length=1)
    line_1: str = Field(min_length=1)
    line_2: str | None = None
    city: str = Field(min_length=1)
    postal_code: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)


class CreateOrderRequest(BaseModel):
    """Validated payload accepted by the order-creation endpoint."""

    customer_id: UUID
    items: list[OrderItemRequest] = Field(min_length=1)
    shipping_address: ShippingAddressRequest
    payment_method: str = Field(min_length=1)
