"""HTTP endpoints owned by the Ordering context."""

from typing import Annotated
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, Response, status
from fastapi.responses import JSONResponse

from ordering.application.messagebus import MessageBus
from ordering.domain.commands import (
    CreateOrder,
    CreateOrderItem,
    CreateOrderShippingAddress,
)
from ordering.domain.order import Money, Order, OrderItem
from ordering.exceptions import OrderingException
from ordering.presentation.dependencies import get_ordering_messagebus
from ordering.presentation.dependencies import get_order_repository
from ordering.application.views import get_order, list_orders
from ordering.presentation.schema.requests import CreateOrderRequest
from ordering.presentation.schema.responses import (
    MoneyResponse,
    OrderItemResponse,
    OrderResponse,
    OrderListResponse,
)

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
logger = logging.getLogger(__name__)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(order_id: UUID, repository=Depends(get_order_repository)) -> OrderResponse | JSONResponse:
    try:
        return _to_order_response(await get_order(order_id, repository))
    except OrderingException as exc:
        return _to_error_response(exc)


@router.get("", response_model=OrderListResponse)
async def list_order_endpoint(
    customer_id: UUID,
    cursor: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    repository=Depends(get_order_repository),
) -> OrderListResponse | JSONResponse:
    try:
        orders, next_cursor = await list_orders(customer_id, limit, cursor, repository)
        return OrderListResponse(items=[_to_order_response(order) for order in orders], next_cursor=next_cursor)
    except OrderingException as exc:
        return _to_error_response(exc)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def post_order(
    request: CreateOrderRequest,
    response: Response,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
    messagebus: Annotated[MessageBus, Depends(get_ordering_messagebus)],
) -> OrderResponse | JSONResponse:
    """Create an order through the Ordering application command bus."""

    command = CreateOrder(
        customer_id=request.customer_id,
        items=tuple(
            CreateOrderItem(product_id=item.product_id, quantity=item.quantity)
            for item in request.items
        ),
        shipping_address=CreateOrderShippingAddress(
            recipient_name=request.shipping_address.recipient_name,
            line_1=request.shipping_address.line_1,
            line_2=request.shipping_address.line_2,
            city=request.shipping_address.city,
            postal_code=request.shipping_address.postal_code,
            country_code=request.shipping_address.country_code,
        ),
        payment_method=request.payment_method,
        idempotency_key=idempotency_key,
    )
    try:
        order = await messagebus.handle(command)
    except OrderingException as exc:
        logger.warning(
            "ordering.order_creation_rejected",
            extra={
                "context": "ordering",
                "operation": "create_order",
                "error_code": exc.code,
            },
        )
        return _to_error_response(exc)
    response.headers["Location"] = f"/api/v1/orders/{order.id}"
    return _to_order_response(order)


def _to_error_response(exc: OrderingException) -> JSONResponse:
    """Map propagated Ordering failures to the public HTTP contract."""

    message = str(exc) if exc.expose_message else "The service is temporarily unavailable."
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": message, "details": {}}},
    )


def _to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        items=[_to_order_item_response(item) for item in order.items],
        total=_to_money_response(order.total),
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def _to_order_item_response(item: OrderItem) -> OrderItemResponse:
    return OrderItemResponse(
        product_id=item.product_id,
        product_name=item.product_name,
        unit_price=_to_money_response(item.unit_price),
        quantity=item.quantity,
        subtotal=_to_money_response(item.subtotal),
    )


def _to_money_response(money: Money) -> MoneyResponse:
    return MoneyResponse(amount=str(money.amount), currency=money.currency)
