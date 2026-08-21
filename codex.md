# Codex Project Instructions

## Project and source of truth

This repository is a Python 3.13 backend for an online-shop order-fulfillment workflow. It uses FastAPI, MongoDB, domain-driven design, RabbitMQ integration events, and a modular-monolith architecture. Version 1 is not a production marketplace or production-ready authentication system.

The documentation under `docs/` is authoritative. Before changing code, read:

1. `docs/README.md` and the documents it selects for the affected feature.
2. `docs/requirements/open-questions.md` for accepted scope and domain decisions.
3. The relevant requirement IDs, bounded-context, aggregate, API, event, and database documents.
4. Every accepted ADR relevant to the change.

Keep requirements, public contracts, tests, and ADRs synchronized with behavior. If documents conflict, report the conflict and stop rather than guessing. If recovery semantics are undocumented and could alter business state or data, preserve the evidence and ask for a decision.

## Non-negotiable architecture rules

- Build one modular monolith with Catalog, Ordering, Inventory, Payment, and Fulfillment bounded contexts.
- Keep dependencies pointing inward: presentation -> application -> domain; infrastructure implements inward-defined ports.
- Domain code must not depend on FastAPI, HTTP/Pydantic schemas, MongoDB, RabbitMQ, Redis, or infrastructure implementations.
- Do not import another context's domain, aggregate, repository, persistence model, infrastructure, or internal application service.
- Cross-context business progression uses versioned integration events. Read-only composition may use a documented application contract, never another context's database or aggregate.
- Keep routers thin. Put business invariants and state transitions in aggregates, value objects, policies, or domain services.
- Use explicit mappings between domain objects, HTTP schemas, integration-event contracts, and MongoDB documents.
- Add a shared abstraction only after at least two contexts need the same stable concept.
- Create package directories when a vertical slice becomes real; do not scaffold large sets of empty files.

The intended package shape is `online_shop/`, with `shared/` and one `{domain,application,infrastructure,presentation}` package per bounded context.

## Domain and data invariants

- Support EUR only. Represent money with `Decimal` semantics, never binary floating point.
- Use timezone-aware UTC timestamps.
- Change aggregate state through behavior, never public status assignment.
- Order lines and shipping addresses are immutable snapshots. Later Catalog changes must not alter existing orders.
- Confirmation requires both a successful inventory reservation and payment authorization. An order cannot be cancelled after shipment.
- Prevent inventory overselling with optimistic concurrency. A negative adjustment must not reduce on-hand stock below reserved stock.
- Use one reservation record per order. Process multi-item reservations deterministically and compensate partial work idempotently.
- Active, uncommitted reservations expire after 24 hours by changing state and releasing stock once.
- A successful fake-payment authorization is the completed charge; there is no capture operation. Refund at most once.
- Create at most one shipment per order.
- Generate SKUs as exactly 20 cryptographically random ASCII letters (`A-Z`, `a-z`); keep them globally unique, immutable, and never reusable.
- Do not physically delete application records. Model expiration through status and timestamps; do not use MongoDB TTL deletion indexes.

The exact choices between `PENDING` and immediate `AWAITING_INVENTORY`, and between `PAYMENT_FAILED` and `CANCELLED`, remain unresolved in the documentation. Obtain a domain decision before implementing behavior that depends on either choice.

## Persistence, messaging, and reliability

- Use PyMongo's asynchronous API and explicit domain/document mappers. Each context owns a separate logical MongoDB database and its collections.
- Store a numeric version on `Order` and `InventoryItem`; update by aggregate ID plus expected version. A zero-document match is a typed concurrency conflict, not a successful no-op.
- Persist an aggregate change and its outgoing event atomically through a local MongoDB transactional Outbox. MongoDB must run as a replica set where transactions are required; never silently weaken this guarantee.
- Do not use cross-context transactions, essential FastAPI background tasks, Celery, or Redis in version 1.
- Use direct asynchronous RabbitMQ consumers and assume at-least-once, unordered, duplicate delivery.
- Consumers deduplicate durably by consumer and `event_id`, and acknowledge only after business changes and Inbox state are durable.
- Integration events use the documented envelope and catalog. Additive fields may retain an event version; breaking changes increment `event_version`.
- Retry only explicitly transient failures, with bounded exponential backoff. Retain exhausted records in an inspectable failed state and emit the relevant metric.
- Never expose or log secrets, payment tokens, raw driver errors, or stack traces.

## API and security contract

- Use `/api/v1`, opaque IDs, ISO 8601 UTC timestamps, decimal-string money values, and the common machine-readable error envelope in `docs/api/api-overview.md`.
- Propagate or create `X-Correlation-ID` and echo it to clients.
- `POST /api/v1/orders` requires `Idempotency-Key`. Scope it by customer and route for 24 hours; identical replay returns the stored response and a changed payload returns `409`.
- Return `201 Created` with `Location` only after the Order and `OrderPlaced` Outbox record are durably persisted. Downstream work remains asynchronous.
- Customer APIs accept a trusted `customer_id`; version 1 has no customer authentication or ownership enforcement. Never describe this as production-ready security.
- Admin mutations require the environment-provided `X-Admin-Key`; missing or invalid keys return `401`.
- Register development payment-control endpoints only in development/test.
- Validate all external input and map FastAPI validation errors into the project error envelope.
- Keep order listing newest-first with required `customer_id`, cursor pagination, default limit 20, and maximum 100. Do not add optional filtering or sorting without a requirement.

## Implementation workflow

For each significant vertical slice:

1. Identify the requirement IDs and owning bounded context.
2. State the affected invariants and API/event contracts.
3. Add or update domain and application tests.
4. Implement domain behavior first.
5. Implement the command/query handler and inward-defined ports.
6. Add persistence or messaging adapters.
7. Add the HTTP or event entry point last.
8. Run focused checks, then the relevant wider suite.
9. Update requirements, contracts, and ADRs when behavior or architecture changes.

Bug fixes should include a focused regression test when practical. Avoid speculative abstractions and unrelated refactors.

## Testing and tooling

Domain tests must run without FastAPI, MongoDB, RabbitMQ, or Redis. Use fakes for application tests and disposable MongoDB replica-set/RabbitMQ containers for integration and end-to-end tests. Inject time, UUID, tracking-number, and fake-gateway controls so tests remain deterministic. Always cover relevant success, invalid-state, duplicate-delivery, compensation, and concurrency paths.

Use `uv` for environment/dependency management, Ruff for linting and formatting, mypy for type checking, and pytest/pytest-asyncio for tests. The repository is currently a scaffold, so these commands become authoritative once their configuration and dependencies exist:

```text
uv sync
uv run uvicorn online_shop.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

At handoff, report assumptions, changed files, checks run, and remaining risks. Do not claim a check passed unless it was actually run.
