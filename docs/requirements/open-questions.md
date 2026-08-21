# Decision Register

The recommended defaults were accepted on **2026-08-21**. The following decisions are authoritative for version 1.

## Accepted decisions

| ID | Decision |
|---|---|
| OQ-01 | Version 1 has no customer authentication. APIs accept a trusted `customer_id`; production identity and ownership checks are future work. |
| OQ-02 | Use one MongoDB deployment with a separate logical database per bounded context. |
| OQ-03 | Use direct asynchronous RabbitMQ consumers; do not use Celery. |
| OQ-04 | Support EUR only in version 1 and reject mixed or unsupported currencies. |
| OQ-05 | Store one inventory reservation record per order. Multi-item reservation failures trigger idempotent compensation for any items already reserved. |
| OQ-06 | Cancellation is allowed through `CONFIRMED` only while no shipment is `SHIPPED`; release inventory and refund an authorized payment when applicable. |
| OQ-07 | Protect admin endpoints in development with an environment-provided `X-Admin-Key`. This is temporary and not production authentication. |
| OQ-08 | Use cursor pagination with a default page size of 20 and maximum of 100. |
| OQ-09 | Scope order idempotency keys by customer and route and retain them for 24 hours. |
| OQ-10 | Control fake payment outcomes through documented test-token conventions and development-only approve/fail endpoints. |
| OQ-11 | Event-schema changes may be additive within a version; breaking changes increment `event_version`. Consumers ignore unknown additive fields. |
| OQ-12 | Use exponential-backoff Outbox retries with a bounded attempt count. Exhausted records enter an inspectable failed state and raise a metric. Exact timing/count values belong to configuration. |
| OQ-13 | Redis is not part of version 1. Add it only after an accepted ADR identifies a measured need. |
| OQ-14 | Version 1 requires structured logs, correlation IDs, health endpoints, and Prometheus metrics. OpenTelemetry tracing is optional if time permits. |
| OQ-15 | Inventory extraction is a stretch goal only after the modular monolith is complete and tested. |
| OQ-16 | Keep the repository/package identity `online-shop`; MarketFlow may be used later as a presentation name without changing technical identifiers. |

## Resolved clarifications

| ID | Decision |
|---|---|
| RC-01 | Generate each SKU as exactly 20 cryptographically random ASCII English letters (`A-Z`, `a-z`). Enforce global uniqueness and never reuse a SKU, including after product deactivation. Retry generation on the unlikely unique-index collision. |
| RC-02 | Reject atomically any negative adjustment that would make on-hand quantity lower than reserved quantity. Return `409 Conflict` and leave inventory unchanged. |
| RC-03 | An active inventory reservation expires 24 hours after creation. A worker idempotently marks it `EXPIRED`, releases held inventory, and emits an expiration/release event. Never delete the reservation record. Committed, released, or already-expired reservations are unaffected. |
| RC-04 | Use a single-step fake payment: successful authorization represents the completed test charge. There is no separate capture operation. Cancellation refunds the authorized charge once. |
| RC-05 | Shipment `ship` and `deliver` transitions are manual admin actions only in version 1. No carrier webhook is included. |
| RC-06 | Use the HTTP error mapping documented in `api/api-overview.md`, with a stable machine-readable error code for every error response. |
| RC-07 | Do not add optional order sorting or filtering. The only list scope is required `customer_id`, with fixed newest-first order and cursor pagination. |
| RC-08 | Never physically delete application records. Retry only explicitly retryable transient failures. After bounded retries, preserve an inspectable failed state. If recovery semantics are unclear and materially affect state or data, Codex must ask the user rather than invent a policy. |
| RC-09 | `POST /api/v1/orders` returns `201 Created` after the Order and its Outbox event are durably persisted. Downstream processing remains asynchronous. |

All previously listed `RC-*` clarifications are resolved. Because authentication is excluded from version 1, customer ownership/privacy enforcement remains explicitly out of scope. State this limitation in the public README and do not describe version 1 as production-ready security.
