# Domain Model

## Ubiquitous language

- **Order:** a customer's intent to buy snapshotted products at a recorded price.
- **Reservation:** inventory held for one order before fulfillment is committed.
- **Authorization:** a single-step successful fake charge. There is no separate capture operation; an authorized charge can be refunded once.
- **Confirmation:** the point at which inventory and payment prerequisites are satisfied.
- **Shipment:** fulfillment record created for a confirmed order.
- **Compensation:** a business action reversing an earlier step, such as release or refund.

## Order lifecycle

```text
PENDING -> AWAITING_INVENTORY -> AWAITING_PAYMENT -> CONFIRMED
                                                      |
                                                      v
FULFILLING -> SHIPPED -> DELIVERED

Failure terminals/alternates: REJECTED, PAYMENT_FAILED, CANCELLED
```

The exact choice between `PENDING` and immediately `AWAITING_INVENTORY`, and between `PAYMENT_FAILED` and `CANCELLED`, should be finalized before implementation to avoid redundant states.

## Core value objects

- `Money(amount: Decimal, currency: Currency)`; non-negative for prices, same currency for arithmetic, and EUR is the only accepted version-1 currency.
- `OrderId`, `CustomerId`, `ProductId`, `PaymentId`, `ShipmentId`.
- `Quantity`; strictly positive for order lines, signed type only for adjustments.
- `ShippingAddress`; required normalized fields, immutable snapshot.
- `SKU`; exactly 20 cryptographically random ASCII English letters (`A-Z`, `a-z`), globally unique, immutable, and never reusable.
- `IdempotencyKey`; validated opaque value.

## Key invariants

- An order contains at least one line; quantities are positive; prices are non-negative.
- Items cannot change after placement/confirmation as defined by the final state machine.
- Confirmation requires both inventory reservation and payment authorization.
- Cancellation is impossible once shipped.
- Cancellation is allowed through `CONFIRMED` while the shipment has not reached `SHIPPED`, with inventory release and payment compensation when applicable.
- Inventory available quantity never becomes negative.
- A stock adjustment cannot reduce on-hand quantity below reserved quantity.
- A reservation is applied, released, or committed at most once.
- An active, uncommitted reservation expires 24 hours after creation; expiration releases stock without deleting history.
- Payment authorization/refund is idempotent and never exceeds the order amount.
- Shipment creation occurs at most once per order.

State transitions occur through behavior (`order.confirm()`), never public status assignment.
