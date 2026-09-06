from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pymongo.errors import DuplicateKeyError
from ordering.application.create_order import create_order
from ordering.application.idempotency import (
    IdempotencyConflictError,
    IdempotencyKeyAlreadyExistsError,
)
from ordering.application.uow import OrderingUowAbs
from ordering.domain.commands import (
    CreateOrder,
    CreateOrderItem,
    CreateOrderShippingAddress,
)
from ordering.domain.idempotency import IdempotencyRecord
from ordering.domain.order import Currency, OrderStatus
from ordering.domain.repository import IdempotencyRepositoryAbs, OrderRepositoryAbs


class RecordingOrderRepository(OrderRepositoryAbs):
    def __init__(self) -> None:
        self.orders = {}

    async def add(self, order) -> None:
        self.orders[order.id] = order

    async def get(self, order_id):
        return self.orders.get(order_id)


class RecordingIdempotencyRepository(IdempotencyRepositoryAbs):
    def __init__(self) -> None:
        self.records = {}

    async def deactivate_expired(self, customer_id, route, key, now: datetime) -> None:
        record = self.records.get((customer_id, route, key))
        if record is not None and record.expires_at <= now:
            del self.records[(customer_id, route, key)]

    async def get_active(self, customer_id, route, key, now: datetime):
        return self.records.get((customer_id, route, key))

    async def add(self, record: IdempotencyRecord) -> None:
        self.records[(record.customer_id, record.route, record.key)] = record


class DuplicateOrderRepository(RecordingOrderRepository):
    async def add(self, order) -> None:
        raise DuplicateKeyError("duplicate order document")


class DuplicateOnceIdempotencyRepository(RecordingIdempotencyRepository):
    def __init__(self) -> None:
        super().__init__()
        self.duplicate_raised = False

    async def add(self, record: IdempotencyRecord) -> None:
        if not self.duplicate_raised:
            self.duplicate_raised = True
            raise IdempotencyKeyAlreadyExistsError
        await super().add(record)


class RecordingUow(OrderingUowAbs):
    def __init__(self) -> None:
        self.active = False
        self.entered_count = 0
        self.exited_count = 0
        self.committed = False
        self._orders_before_transaction = None
        self._idempotency_records_before_transaction = None
        self.orders = RecordingOrderRepository()
        self.idempotency = RecordingIdempotencyRepository()

    async def __aenter__(self) -> "RecordingUow":
        if self.active:
            raise RuntimeError("This unit of work is already active.")
        self.active = True
        self.entered_count += 1
        self._orders_before_transaction = self.orders.orders.copy()
        self._idempotency_records_before_transaction = self.idempotency.records.copy()
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        if exc_type is not None:
            self.orders.orders = self._orders_before_transaction
            self.idempotency.records = self._idempotency_records_before_transaction
        self.active = False
        self.exited_count += 1
        return None

    async def commit(self) -> None:
        if not self.active:
            raise RuntimeError("This unit of work has not been entered.")
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
    assert item.product_name == f"Mock Product {str(command.items[0].product_id)[:8]}"
    assert item.quantity == 1
    assert item.unit_price.amount == Decimal("29.99")
    assert item.subtotal.amount == Decimal("29.99")
    assert item.unit_price.currency is Currency.EUR
    assert item.subtotal.currency is Currency.EUR
    assert order.total == item.subtotal
    assert order.customer_id == command.customer_id
    assert item.product_id == command.items[0].product_id
    assert order.shipping_address.recipient_name == "Test Customer"
    assert uow.orders.orders[order.id] is order
    assert uow.committed
    assert uow.entered_count == 1
    assert uow.exited_count == 1
    assert not uow.active


@pytest.mark.asyncio
async def test_create_order_replays_the_original_order_for_an_identical_key() -> None:
    command = CreateOrder(
        customer_id=uuid4(),
        items=(CreateOrderItem(product_id=uuid4(), quantity=2),),
        shipping_address=CreateOrderShippingAddress(
            recipient_name="Test Customer",
            line_1="1 Test Street",
            city="Tehran",
            postal_code="1234567890",
            country_code="IR",
        ),
        payment_method="test-token",
        idempotency_key="same-key",
    )
    uow = RecordingUow()

    created = await create_order(command, uow)
    replayed = await create_order(command, uow)

    assert replayed is created
    assert len(uow.orders.orders) == 1


@pytest.mark.asyncio
async def test_create_order_rejects_a_different_request_for_an_active_key() -> None:
    command = CreateOrder(
        customer_id=uuid4(),
        items=(CreateOrderItem(product_id=uuid4(), quantity=1),),
        shipping_address=CreateOrderShippingAddress(
            recipient_name="Test Customer",
            line_1="1 Test Street",
            city="Tehran",
            postal_code="1234567890",
            country_code="IR",
        ),
        payment_method="test-token",
        idempotency_key="same-key",
    )
    uow = RecordingUow()
    await create_order(command, uow)

    with pytest.raises(IdempotencyConflictError, match="different order request"):
        await create_order(
            command.model_copy(update={"payment_method": "different-token"}), uow
        )


@pytest.mark.asyncio
async def test_concurrent_same_key_retries_after_a_duplicate_idempotency_insert() -> None:
    command = CreateOrder(
        customer_id=uuid4(),
        items=(CreateOrderItem(product_id=uuid4(), quantity=1),),
        shipping_address=CreateOrderShippingAddress(
            recipient_name="Test Customer",
            line_1="1 Test Street",
            city="Tehran",
            postal_code="1234567890",
            country_code="IR",
        ),
        payment_method="test-token",
        idempotency_key="same-key",
    )
    uow = RecordingUow()
    uow.idempotency = DuplicateOnceIdempotencyRepository()

    order = await create_order(command, uow)

    assert uow.idempotency.duplicate_raised
    assert len(uow.orders.orders) == 1
    assert order.id in uow.orders.orders
    assert uow.entered_count == 2
    assert uow.exited_count == 2


@pytest.mark.asyncio
async def test_unrelated_duplicate_key_errors_are_not_retried() -> None:
    command = CreateOrder(
        customer_id=uuid4(),
        items=(CreateOrderItem(product_id=uuid4(), quantity=1),),
        shipping_address=CreateOrderShippingAddress(
            recipient_name="Test Customer",
            line_1="1 Test Street",
            city="Tehran",
            postal_code="1234567890",
            country_code="IR",
        ),
        payment_method="test-token",
        idempotency_key="same-key",
    )
    uow = RecordingUow()
    uow.orders = DuplicateOrderRepository()

    with pytest.raises(DuplicateKeyError, match="duplicate order document"):
        await create_order(command, uow)

    assert uow.entered_count == 1
    assert uow.exited_count == 1
