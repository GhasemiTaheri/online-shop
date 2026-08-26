from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

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
from ordering.infrastructure.mongodb_mapper import order_from_document, order_to_document
from ordering.infrastructure.mongodb_repository import MongoOrderRepository


class FakeCollection:
    def __init__(self) -> None:
        self.inserted_document = None
        self.inserted_session = None
        self.document = None
        self.find_filter = None
        self.find_session = None

    async def insert_one(self, document, session) -> None:
        self.inserted_document = document
        self.inserted_session = session

    async def find_one(self, filter, session):
        self.find_filter = filter
        self.find_session = session
        return self.document


def _order() -> Order:
    now = datetime.now(UTC)
    price = Money(amount=Decimal("29.99"), currency=Currency.EUR)
    item = OrderItem(
        product_id=ProductId(uuid4()),
        product_name="T-Shirt",
        unit_price=price,
        quantity=2,
        subtotal=Money(amount=Decimal("59.98"), currency=Currency.EUR),
    )
    return Order(
        id=OrderId(uuid4()),
        customer_id=CustomerId(uuid4()),
        items=(item,),
        shipping_address=ShippingAddress(
            recipient_name="Test Customer",
            line_1="1 Test Street",
            line_2="Unit 2",
            city="Tehran",
            postal_code="1234567890",
            country_code="IR",
        ),
        total=item.subtotal,
        status=OrderStatus.PENDING,
        version=1,
        created_at=now,
        updated_at=now,
    )


def test_order_mapper_round_trips_the_persisted_fields() -> None:
    order = _order()

    document = order_to_document(order)
    restored = order_from_document(document)

    assert document["_id"] == str(order.id)
    assert document["total"] == {"amount": "59.98", "currency": "EUR"}
    assert restored.id == order.id
    assert restored.customer_id == order.customer_id
    assert restored.items == order.items
    assert restored.shipping_address == order.shipping_address
    assert restored.total == order.total
    assert restored.status is OrderStatus.PENDING
    assert restored.created_at == order.created_at


@pytest.mark.asyncio
async def test_repository_uses_the_uow_session_for_writes_and_reads() -> None:
    collection = FakeCollection()
    session = object()
    repository = MongoOrderRepository(collection, lambda: session)
    order = _order()

    await repository.add(order)
    collection.document = collection.inserted_document
    restored = await repository.get(order.id)

    assert collection.inserted_document == order_to_document(order)
    assert collection.inserted_session is session
    assert collection.find_filter == {"_id": str(order.id)}
    assert collection.find_session is session
    assert restored is not None
    assert restored.id == order.id
