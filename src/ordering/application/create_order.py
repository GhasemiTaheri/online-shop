"""Order-creation use case."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from uuid import uuid4

from ordering.application.idempotency import (
    ORDER_CREATE_ROUTE,
    IdempotencyConflictError,
    IdempotencyRecord,
)
from ordering.application.uow import OrderingUowAbs
from ordering.domain.commands import CreateOrder
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


async def create_order(command: CreateOrder, uow: OrderingUowAbs) -> Order:
    """Persist a user-supplied order with replay-safe idempotency."""

    now = datetime.now(UTC)
    customer_id = CustomerId(command.customer_id)
    fingerprint = _request_fingerprint(command)
    await uow.idempotency.deactivate_expired(
        customer_id, ORDER_CREATE_ROUTE, command.idempotency_key, now
    )
    existing = await uow.idempotency.get_active(
        customer_id, ORDER_CREATE_ROUTE, command.idempotency_key, now
    )
    if existing is not None:
        if existing.request_fingerprint != fingerprint:
            raise IdempotencyConflictError(
                "Idempotency-Key has already been used for a different order request."
            )
        order = await uow.orders.get(existing.order_id)
        if order is None:
            raise RuntimeError("The idempotency record references a missing order.")
        return order

    items = tuple(_mock_order_item(item.product_id, item.quantity) for item in command.items)
    total = Money(
        amount=sum((item.subtotal.amount for item in items), Decimal("0")),
        currency=Currency.EUR,
    )
    order = Order(
        id=OrderId(uuid4()),
        customer_id=customer_id,
        items=items,
        shipping_address=ShippingAddress(
            recipient_name=command.shipping_address.recipient_name,
            line_1=command.shipping_address.line_1,
            line_2=command.shipping_address.line_2,
            city=command.shipping_address.city,
            postal_code=command.shipping_address.postal_code,
            country_code=command.shipping_address.country_code,
        ),
        total=total,
        status=OrderStatus.PENDING,
        version=1,
        created_at=now,
        updated_at=now,
    )
    async with uow:
        await uow.orders.add(order)
        await uow.idempotency.add(
            IdempotencyRecord(
                customer_id=customer_id,
                route=ORDER_CREATE_ROUTE,
                key=command.idempotency_key,
                request_fingerprint=fingerprint,
                order_id=order.id,
                expires_at=now + timedelta(hours=24),
            )
        )
        await uow.commit()
    return order


def _mock_order_item(product_id, quantity: int) -> OrderItem:
    """Create a temporary Catalog snapshot until the Catalog context is available."""

    unit_price = Money(amount=Decimal("29.99"), currency=Currency.EUR)
    return OrderItem(
        product_id=ProductId(product_id),
        product_name=f"Mock Product {str(product_id)[:8]}",
        unit_price=unit_price,
        quantity=quantity,
        subtotal=Money(
            amount=unit_price.amount * quantity,
            currency=Currency.EUR,
        ),
    )


def _request_fingerprint(command: CreateOrder) -> str:
    """Hash the idempotent request without persisting its payment token."""

    payload = {
        "customer_id": str(command.customer_id),
        "items": [item.model_dump(mode="json") for item in command.items],
        "shipping_address": command.shipping_address.model_dump(mode="json"),
        "payment_method": command.payment_method,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()
