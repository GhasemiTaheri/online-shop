from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ordering.application.create_order import create_order
from ordering.application.uow import OrderingUowAbs
from ordering.domain.commands import CreateOrder
from ordering.domain.idempotency import IdempotencyRecord
from ordering.domain.order import Order
from ordering.domain.repository import IdempotencyRepositoryAbs, OrderRepositoryAbs
from ordering.presentation.dependencies import get_ordering_messagebus
from ordering.presentation.orders import router
from shared.presentation.middleware import install_correlation_middleware


class NullOrderRepository(OrderRepositoryAbs):
    def __init__(self) -> None:
        self.orders = {}

    async def add(self, order: Order) -> None:
        self.orders[order.id] = order

    async def get(self, order_id):
        return self.orders.get(order_id)


class NullIdempotencyRepository(IdempotencyRepositoryAbs):
    def __init__(self) -> None:
        self.records = {}

    async def deactivate_expired(self, customer_id, route, key, now) -> None:
        return None

    async def get_active(self, customer_id, route, key, now):
        return self.records.get((customer_id, route, key))

    async def add(self, record: IdempotencyRecord) -> None:
        self.records[(record.customer_id, record.route, record.key)] = record


class RecordingUow(OrderingUowAbs):
    def __init__(self) -> None:
        self.orders = NullOrderRepository()
        self.idempotency = NullIdempotencyRepository()

    async def __aenter__(self) -> "RecordingUow":
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


class RecordingMessageBus:
    def __init__(self) -> None:
        self.command: CreateOrder | None = None
        self.uow = RecordingUow()

    async def handle(self, command: CreateOrder) -> Order:
        self.command = command
        return await create_order(command, self.uow)


def _app_with_bus(messagebus: RecordingMessageBus) -> FastAPI:
    app = FastAPI()
    install_correlation_middleware(app)
    app.include_router(router)
    app.dependency_overrides[get_ordering_messagebus] = lambda: messagebus
    return app


def _valid_payload() -> dict[str, object]:
    return {
        "customer_id": str(uuid4()),
        "items": [{"product_id": str(uuid4()), "quantity": 2}],
        "shipping_address": {
            "recipient_name": "Test Customer",
            "line_1": "1 Test Street",
            "line_2": None,
            "city": "Tehran",
            "postal_code": "1234567890",
            "country_code": "IR",
        },
        "payment_method": "test-token",
    }


def test_post_order_dispatches_a_complete_command_and_returns_created_order() -> None:
    messagebus = RecordingMessageBus()
    payload = _valid_payload()

    response = TestClient(_app_with_bus(messagebus)).post(
        "/api/v1/orders", headers={"Idempotency-Key": "test-key"}, json=payload
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["items"][0]["product_name"].startswith("Mock Product ")
    assert body["total"] == {"amount": "59.98", "currency": "EUR"}
    assert "payment_method" not in body
    assert response.headers["location"] == f"/api/v1/orders/{body['id']}"
    assert messagebus.command is not None
    assert str(messagebus.command.customer_id) == payload["customer_id"]
    assert str(messagebus.command.items[0].product_id) == payload["items"][0]["product_id"]
    assert messagebus.command.items[0].quantity == 2
    assert messagebus.command.shipping_address.line_2 is None
    assert messagebus.command.payment_method == "test-token"
    assert messagebus.command.idempotency_key == "test-key"


def test_post_order_rejects_invalid_input_before_dispatch() -> None:
    messagebus = RecordingMessageBus()
    payload = _valid_payload()
    payload["items"] = []

    response = TestClient(_app_with_bus(messagebus)).post(
        "/api/v1/orders",
        headers={"Idempotency-Key": "test-key"},
        json=payload,
    )

    assert response.status_code == 422
    assert messagebus.command is None


def test_post_order_requires_a_non_empty_idempotency_key() -> None:
    messagebus = RecordingMessageBus()

    response = TestClient(_app_with_bus(messagebus)).post(
        "/api/v1/orders", json=_valid_payload()
    )

    assert response.status_code == 422
    assert messagebus.command is None


def test_post_order_echoes_the_supplied_correlation_id() -> None:
    response = TestClient(_app_with_bus(RecordingMessageBus())).post(
        "/api/v1/orders",
        headers={"Idempotency-Key": "test-key", "X-Correlation-ID": "workflow-123"},
        json=_valid_payload(),
    )

    assert response.status_code == 201
    assert response.headers["x-correlation-id"] == "workflow-123"


def test_post_order_returns_conflict_for_a_different_replay() -> None:
    messagebus = RecordingMessageBus()
    app = _app_with_bus(messagebus)
    payload = _valid_payload()
    client = TestClient(app)

    first = client.post(
        "/api/v1/orders", headers={"Idempotency-Key": "same-key"}, json=payload
    )
    payload["payment_method"] = "different-token"
    replay = client.post(
        "/api/v1/orders", headers={"Idempotency-Key": "same-key"}, json=payload
    )

    assert first.status_code == 201
    assert replay.status_code == 409
    assert replay.json() == {
        "error": {
            "code": "ORDERING_CONFLICT",
            "message": "Idempotency-Key has already been used for a different order request.",
            "details": {},
        }
    }
