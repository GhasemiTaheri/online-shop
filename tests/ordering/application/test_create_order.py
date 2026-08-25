from datetime import UTC
from decimal import Decimal

from ordering.application.create_order import create_order
from ordering.domain.order import Currency, OrderStatus


def test_create_order_returns_a_pending_order_with_snapshotted_item_data() -> None:
    order = create_order()

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
