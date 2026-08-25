"""HTTP endpoints owned by the Ordering context."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

from ordering.application.idempotency import IdempotencyConflictError
from ordering.application.messagebus import MessageBus
from ordering.domain.commands import (
    CreateOrder,
    CreateOrderItem,
    CreateOrderShippingAddress,
)
from ordering.domain.order import Money, Order, OrderItem
from ordering.presentation.dependencies import get_ordering_messagebus
from ordering.presentation.schema.requests import CreateOrderRequest
from ordering.presentation.schema.responses import (
    MoneyResponse,
    OrderItemResponse,
    OrderResponse,
)

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def post_order(
    request: CreateOrderRequest,
    response: Response,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=1)],
    messagebus: Annotated[MessageBus, Depends(get_ordering_messagebus)],
) -> OrderResponse:
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
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    response.headers["Location"] = f"/api/v1/orders/{order.id}"
    return _to_order_response(order)


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
