"""Response schemas for Ordering HTTP endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MoneyResponse(BaseModel):
    amount: str
    currency: str


class OrderItemResponse(BaseModel):
    product_id: UUID
    product_name: str
    unit_price: MoneyResponse
    quantity: int
    subtotal: MoneyResponse


class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    items: list[OrderItemResponse]
    total: MoneyResponse
    status: str
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    next_cursor: str | None
