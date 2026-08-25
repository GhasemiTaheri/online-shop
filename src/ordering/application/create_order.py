"""Order-creation use case."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

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
    """Create the current mock order and commit the use-case transaction."""

    del command
    now = datetime.now(UTC)
    unit_price = Money(amount=Decimal("29.99"), currency=Currency.EUR)
    item = OrderItem(
        product_id=ProductId(uuid4()),
        product_name="Mock T-Shirt",
        unit_price=unit_price,
        quantity=2,
        subtotal=Money(amount=Decimal("59.98"), currency=Currency.EUR),
    )
    order = Order(
        id=OrderId(uuid4()),
        customer_id=CustomerId(uuid4()),
        items=(item,),
        shipping_address=ShippingAddress(
            recipient_name="Mock Customer",
            line_1="123 Example Street",
            line_2=None,
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
    await uow.commit()
    return order
