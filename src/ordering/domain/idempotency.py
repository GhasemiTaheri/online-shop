"""Domain idempotency state owned by the Ordering context."""

from dataclasses import dataclass
from datetime import datetime

from ordering.domain.order import CustomerId, OrderId


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """The durable result of an idempotent command within its active window."""

    customer_id: CustomerId
    route: str
    key: str
    request_fingerprint: str
    order_id: OrderId
    expires_at: datetime
    active: bool = True
