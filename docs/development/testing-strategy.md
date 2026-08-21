# Testing Strategy

## Test pyramid

1. **Domain unit tests:** fast, deterministic, no FastAPI/MongoDB/RabbitMQ/Redis.
2. **Application tests:** handlers with fakes, verifying orchestration, emitted events, and errors.
3. **Repository integration tests:** real MongoDB mappings, indexes, transactions, and optimistic conflicts.
4. **Messaging integration tests:** Outbox publishing, consumer Inbox idempotency, redelivery, retry/dead-letter behavior.
5. **API tests:** request validation, response/error contracts, idempotency, and environment-gated endpoints.
6. **End-to-end tests:** a small set covering happy path and critical compensations with real containers.

## Required scenarios

- Order rejects empty lines, zero quantity, negative price, mixed currency, and invalid transitions.
- Product values are snapshotted and later price changes do not alter old orders.
- Concurrent reservations cannot oversell.
- Repeated order request with same key/body returns the same order; changed body conflicts.
- Duplicate integration event produces one business effect.
- Broker outage leaves a publishable outbox record; retry eventually publishes.
- Inventory rejection terminates the order correctly.
- Payment failure releases inventory.
- Confirmation creates exactly one shipment.
- Shipped orders cannot be cancelled.
- EUR is accepted and unsupported/mixed currencies are rejected.
- Multi-item reservation failure compensates every partial reservation idempotently.
- Admin mutations reject a missing/invalid development admin key.
- Cursor pagination enforces default 20 and maximum 100.
- Exhausted Outbox retries enter an inspectable failed state and increment the failure metric.
- SKU generation produces exactly 20 ASCII letters, survives collision retry, and never reuses a deactivated product's SKU.
- A stock adjustment below reserved quantity returns `409` and leaves all quantities unchanged.
- At 24 hours an active reservation expires and releases stock once; committed/released/expired reservations are no-ops and no record is deleted.
- Payment authorization completes the fake charge without a separate capture step; refund occurs at most once.
- Order creation returns `201` with `Location` only after Order and Outbox persistence succeeds.
- API failures follow the documented HTTP mapping and common error envelope.

## Test environment

Use disposable MongoDB replica-set and RabbitMQ containers for integration/e2e tests. Tests must not depend on developer data. Control time, UUIDs, tracking numbers, and fake gateway outcomes through injected ports.

## Quality gates

Require lint, format check, type check, unit tests, and selected integration tests in CI. Prefer meaningful domain/application coverage over an arbitrary repository-wide percentage. Record load-test conditions and keep benchmarks outside normal unit test runs.
