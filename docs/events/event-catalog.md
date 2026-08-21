# Event Catalog

Integration-event names describe facts in PascalCase. Payloads contain only the data consumers require.

| Event | Producer | Primary consumers | Required payload summary |
|---|---|---|---|
| `OrderPlaced` | Ordering | Inventory | order ID, customer ID, item product IDs/quantities |
| `OrderCancelled` | Ordering | Inventory, Payment | order ID, reason, compensation hints/state |
| `InventoryReserved` | Inventory | Ordering, Payment | order ID, reservation ID, item quantities |
| `InventoryRejected` | Inventory | Ordering | order ID, rejected items/reason code |
| `InventoryReleased` | Inventory | Ordering/operations | order ID, reservation ID |
| `InventoryReservationExpired` | Inventory | Ordering/operations | order ID, reservation ID, expired timestamp |
| `InventoryReservationCommitted` | Inventory | operations | order ID, reservation ID |
| `PaymentAuthorized` | Payment | Ordering, Inventory | order ID, payment ID, amount, provider transaction ID |
| `PaymentFailed` | Payment | Ordering, Inventory | order ID, payment ID, reason code |
| `PaymentRefunded` | Payment | Ordering | order ID, payment ID, amount |
| `OrderConfirmed` | Ordering | Fulfillment | order ID, address snapshot, item snapshot |
| `ShipmentCreated` | Fulfillment | Ordering | order ID, shipment ID, tracking number |
| `ShipmentShipped` | Fulfillment | Ordering | order ID, shipment ID, shipped timestamp |
| `ShipmentDelivered` | Fulfillment | Ordering | order ID, shipment ID, delivered timestamp |

## Rules

- Consumers deduplicate by `event_id` using a durable Inbox/processed-message record.
- Payloads do not expose domain object serialization or payment tokens.
- An event is immutable after publishing.
- Additive fields may be introduced within an event version and consumers ignore unknown fields; breaking schema changes increment `event_version`.
- Domain events may be more detailed and remain internal; only this catalog defines cross-context contracts.
