"""MongoDB document mapping for the Ordering aggregate."""

from typing import Any
from uuid import UUID

from ordering.domain.order import (
    Currency,
    CustomerId,
    Money,
    Order,
    OrderId,
    OrderItem,
    OrderStatus,
    ProductId,
    ShippingAddress,
)


def order_to_document(order: Order) -> dict[str, Any]:
    """Serialize an order into its stable MongoDB document representation."""

    return {
        "_id": str(order.id),
        "customer_id": str(order.customer_id),
        "items": [_order_item_to_document(item) for item in order.items],
        "shipping_address": {
            "recipient_name": order.shipping_address.recipient_name,
            "line_1": order.shipping_address.line_1,
            "line_2": order.shipping_address.line_2,
            "city": order.shipping_address.city,
            "postal_code": order.shipping_address.postal_code,
            "country_code": order.shipping_address.country_code,
        },
        "total": _money_to_document(order.total),
        "status": order.status.value,
        "version": order.version,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


def order_from_document(document: dict[str, Any]) -> Order:
    """Rehydrate an Order aggregate from a MongoDB document."""

    address = document["shipping_address"]
    return Order(
        id=OrderId(UUID(document["_id"])),
        customer_id=CustomerId(UUID(document["customer_id"])),
        items=tuple(_order_item_from_document(item) for item in document["items"]),
        shipping_address=ShippingAddress(
            recipient_name=address["recipient_name"],
            line_1=address["line_1"],
            line_2=address.get("line_2"),
            city=address["city"],
            postal_code=address["postal_code"],
            country_code=address["country_code"],
        ),
        total=_money_from_document(document["total"]),
        status=OrderStatus(document["status"]),
        version=document["version"],
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )


def _order_item_to_document(item: OrderItem) -> dict[str, Any]:
    return {
        "product_id": str(item.product_id),
        "product_name": item.product_name,
        "unit_price": _money_to_document(item.unit_price),
        "quantity": item.quantity,
        "subtotal": _money_to_document(item.subtotal),
    }


def _order_item_from_document(document: dict[str, Any]) -> OrderItem:
    return OrderItem(
        product_id=ProductId(UUID(document["product_id"])),
        product_name=document["product_name"],
        unit_price=_money_from_document(document["unit_price"]),
        quantity=document["quantity"],
        subtotal=_money_from_document(document["subtotal"]),
    )


def _money_to_document(money: Money) -> dict[str, str]:
    return {"amount": str(money.amount), "currency": money.currency.value}


def _money_from_document(document: dict[str, str]) -> Money:
    from decimal import Decimal

    return Money(amount=Decimal(document["amount"]), currency=Currency(document["currency"]))
