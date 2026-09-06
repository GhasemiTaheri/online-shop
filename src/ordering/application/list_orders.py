"""Ordering read use cases and opaque cursor encoding."""

import base64
import binascii
import json
from datetime import datetime
from uuid import UUID

from ordering.domain.order import CustomerId, Order, OrderId
from ordering.domain.repository import OrderRepositoryAbs
from ordering.exceptions import InvalidCursorError, NotFoundException


def encode_cursor(order: Order) -> str:
    payload = {"created_at": order.created_at.isoformat(), "id": str(order.id)}
    return base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")


def decode_cursor(value: str) -> tuple[datetime, UUID]:
    try:
        padded = value + "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode())
        return datetime.fromisoformat(payload["created_at"]), UUID(payload["id"])
    except (ValueError, KeyError, TypeError, binascii.Error, json.JSONDecodeError) as exc:
        raise ValueError("Invalid order cursor.") from exc


async def get_order(order_id: UUID, repository: OrderRepositoryAbs) -> Order:
    order = await repository.get(OrderId(order_id))
    if order is None:
        raise NotFoundException("Order was not found.")
    return order


async def list_orders(customer_id: UUID, limit: int, cursor: str | None,
                      repository: OrderRepositoryAbs) -> tuple[list[Order], str | None]:
    try:
        boundary = decode_cursor(cursor) if cursor else None
    except ValueError as exc:
        raise InvalidCursorError(str(exc)) from exc
    orders = await repository.list_for_customer(CustomerId(customer_id), limit + 1, boundary)
    has_next = len(orders) > limit
    page = orders[:limit]
    return page, encode_cursor(page[-1]) if has_next and page else None
