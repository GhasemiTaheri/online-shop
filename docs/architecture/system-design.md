# System Design

## Happy-path sequence

1. `POST /api/v1/orders` validates input and idempotency.
2. Ordering obtains product snapshots through a Catalog application contract and persists Order + outbox `OrderPlaced` atomically.
3. Publisher sends `OrderPlaced`; Inventory reserves all requested quantities with optimistic concurrency.
4. Inventory writes `InventoryReserved`; Payment creates a payment and calls the fake gateway idempotently.
5. Payment writes `PaymentAuthorized`; Ordering confirms the order.
6. Ordering writes `OrderConfirmed`; Fulfillment creates a shipment and tracking number.

## Failure paths

- **Insufficient inventory:** publish `InventoryRejected`; Ordering rejects the order.
- **Payment failure:** publish `PaymentFailed`; Inventory releases reservation; Ordering records payment failure/cancellation according to the final state policy.
- **Reservation timeout:** after 24 hours, a worker idempotently marks an active uncommitted reservation `EXPIRED`, releases its inventory, and publishes `InventoryReservationExpired`.
- **Duplicate delivery:** Inbox/processed-message record short-circuits an already completed handler.
- **Version conflict:** reload and retry only when the command remains safe; otherwise report a concurrency conflict.
- **Broker unavailable:** aggregate commit remains valid; outbox publisher retries later.
- **Poison message:** exponential backoff with a configurable bounded attempt count, followed by an inspectable failed/dead-letter state and metric.
- **Unspecified failure:** do not invent compensation or deletion behavior; preserve evidence and ask the user for a domain decision.

## Process boundaries

The API and workers may run as separate OS processes from the same codebase. This demonstrates independent scaling/failure behavior without pretending each context is already a microservice.

## Transaction boundaries

- Aggregate document(s), idempotency record when relevant, and outbox record should be committed atomically where MongoDB transaction support is available.
- Do not wrap the full cross-context workflow in a transaction.
- If the local development MongoDB configuration cannot support transactions, fail setup clearly rather than silently weakening the Outbox guarantee.

## Configuration

Settings are environment-based and validated at startup. Expected groups include application, MongoDB per-context database names, RabbitMQ, fake payment behavior, logging, the development admin key, Outbox retry limits, and observability.
