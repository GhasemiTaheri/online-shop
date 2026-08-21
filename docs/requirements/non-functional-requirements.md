# Non-Functional Requirements

## Architecture

- **NFR-01:** Deploy version 1 as one modular monolith with Catalog, Ordering, Inventory, Payment, and Fulfillment bounded contexts.
- **NFR-02:** Each context owns its domain model, repository contract, persistence mapping, and collections.
- **NFR-03:** A context must not import another context's aggregate, repository, persistence model, or internal application service.
- **NFR-04:** Dependencies point inward: presentation -> application -> domain; infrastructure implements inward-defined ports.
- **NFR-05:** Domain code has no dependency on FastAPI, Pydantic HTTP schemas, MongoDB, RabbitMQ, Redis, or infrastructure implementations.

## Reliability and consistency

- **NFR-06:** Messaging assumes at-least-once delivery and unordered duplicates.
- **NFR-07:** Integration events use the transactional Outbox pattern.
- **NFR-08:** Order and InventoryItem persistence use optimistic version checks.
- **NFR-09:** Cross-context MongoDB transactions are prohibited; workflows use events and compensating actions.
- **NFR-10:** Retry policies are bounded and failed messages become inspectable rather than retrying forever.
- **NFR-10A:** Retry only failures classified as transient and retryable. Unknown recovery semantics that could change business state require an explicit user decision before implementation.

## Performance

- **NFR-11:** Under documented local benchmark conditions, p95 read requests target <200 ms and accepted command requests target <300 ms, excluding asynchronous completion.
- **NFR-12:** Queries must be supported by documented MongoDB indexes and pagination.
- **NFR-13:** No performance claim is published without recording dataset size, concurrency, hardware, and benchmark command.

## Security

- **NFR-14:** The system never receives or stores payment-card details; payment methods are opaque test tokens.
- **NFR-15:** Secrets come from environment variables and `.env` files are not committed.
- **NFR-16:** All external input is validated and internal exceptions/stack traces are not exposed.
- **NFR-17:** Development-only payment-control endpoints are disabled outside the development/test environment.
- **NFR-17A:** Admin endpoints require an `X-Admin-Key` matched against an environment-provided secret. This temporary mechanism is not customer authentication and is unsuitable for production.

## Observability

- **NFR-18:** Requests have a correlation ID; events carry event, correlation, causation, and occurrence metadata.
- **NFR-19:** Logs are structured and include relevant aggregate IDs without secrets or payment tokens.
- **NFR-20:** Health checks distinguish liveness from readiness.
- **NFR-21:** Metrics cover request latency/errors, outbox backlog/publish failures, consumer failures, and workflow outcomes.
- **NFR-21A:** OpenTelemetry tracing is optional for version 1; structured logs, correlation IDs, health checks, and Prometheus metrics are mandatory.

## Quality and maintainability

- **NFR-22:** Domain behavior is testable without networked infrastructure.
- **NFR-23:** Type checking, linting, formatting, and tests run through documented commands and CI.
- **NFR-24:** Public contracts, event schemas, requirements, and ADRs change with the behavior they describe.
- **NFR-25:** Timestamps are timezone-aware UTC and money uses decimal minor-unit-safe semantics, never binary floating point.
- **NFR-26:** Application records are retained indefinitely in version 1; no MongoDB TTL index or cleanup task may physically delete them.
