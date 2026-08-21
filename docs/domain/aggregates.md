# Aggregates

## Order (aggregate root)

Contains `OrderId`, `CustomerId`, immutable `OrderItem` snapshots, `ShippingAddress`, total `Money`, status, version, timestamps, and recorded domain events.

Behaviors include `place`, `mark_inventory_reserved`, `reject_for_inventory`, `mark_payment_authorized`, `mark_payment_failed`, `confirm`, `cancel`, `mark_fulfilling`, `mark_shipped`, and `mark_delivered`. Methods enforce transitions and raise facts only after successful state change.

## Product (aggregate root)

Contains `ProductId`, SKU, name, description, price, active flag, version, and timestamps. The application generates a 20-letter cryptographically random SKU and retries on a unique-index collision; the SKU never changes or becomes reusable. Behaviors include create, change price, activate, and deactivate. Existing order snapshots never change when Product changes.

## InventoryItem (aggregate root)

Contains `ProductId`, on-hand/available quantity representation, reserved quantity, references to the per-order reservation record, and version. Behaviors include adjust stock, reserve, release, commit, and expire reservation. A negative adjustment that would make on-hand lower than reserved is rejected without mutation. Optimistic concurrency is mandatory.

One reservation record represents all items requested by an order and has `ACTIVE`, `COMMITTED`, `RELEASED`, or `EXPIRED` status plus `expires_at = created_at + 24 hours`. Multi-product work spans InventoryItem aggregates: the application handler processes items in deterministic order and, on partial failure, idempotently releases every item reserved for that reservation. Concurrency conflicts may retry the whole idempotent reservation command. Expiration changes state and releases stock but never deletes the record.

## Payment (aggregate root)

Contains `PaymentId`, `OrderId`, amount, status (`PENDING`, `AUTHORIZED`, `FAILED`, `REFUNDED`), provider transaction ID, version, and timestamps. Authorization is the completed single-step test charge; there is no `CAPTURED` state or capture command. Behaviors authorize, fail, and refund once. The gateway is a port; the fake adapter belongs to infrastructure.

## Shipment (aggregate root)

Contains `ShipmentId`, `OrderId`, address snapshot, tracking number, status (`CREATED`, `READY`, `SHIPPED`, `DELIVERED`), version, and timestamps. Behaviors ready, ship, and deliver.

## Repository rule

Repositories load and save aggregate roots. Persistence documents and mapping functions remain outside the domain. Expected-version writes that match zero documents produce a typed concurrency error.
