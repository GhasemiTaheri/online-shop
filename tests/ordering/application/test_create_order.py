from datetime import UTC
from decimal import Decimal
from uuid import uuid4

import pytest

from ordering.application.create_order import create_order
from ordering.application.uow import OrderingUowAbs
from ordering.domain.commands import (
    CreateOrder,
    CreateOrderItem,
    CreateOrderShippingAddress,
)
from ordering.domain.order import Currency, OrderStatus


class RecordingUow(OrderingUowAbs):
    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self) -> "RecordingUow":
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None


@pytest.mark.asyncio
async def test_create_order_handler_returns_a_pending_mock_order() -> None:
    command = CreateOrder(
        customer_id=uuid4(),
        items=(CreateOrderItem(product_id=uuid4(), quantity=1),),
        shipping_address=CreateOrderShippingAddress(
            recipient_name="Test Customer",
            line_1="1 Test Street",
            line_2=None,
            city="Tehran",
            postal_code="1234567890",
            country_code="IR",
        ),
        payment_method="test-token",
        idempotency_key="test-key",
    )

    uow = RecordingUow()
    order = await create_order(command, uow)

    assert order.status is OrderStatus.PENDING
    assert order.version == 1
    assert len(order.items) == 1
    assert order.created_at == order.updated_at
    assert order.created_at.tzinfo is UTC

    item = order.items[0]
    assert item.product_name == "Mock T-Shirt"
    assert item.quantity == 2
    assert item.unit_price.amount == Decimal("29.99")
    assert item.subtotal.amount == Decimal("59.98")
    assert item.unit_price.currency is Currency.EUR
    assert item.subtotal.currency is Currency.EUR
    assert order.total == item.subtotal
    assert uow.committed
