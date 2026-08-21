# Architecture Overview

## Style

Version 1 is a modular monolith: one deployable FastAPI application plus worker process(es), with explicit bounded contexts and event contracts. See [ADR-0001](../adr/0001-modular-monolith.md).

```text
Client
  |
FastAPI presentation layer
  |
Application commands and queries
  |
Domain aggregates and policies
  |
Repository / gateway ports
  |
MongoDB adapters + Outbox -> RabbitMQ -> idempotent consumers
```

## Modules

- **Ordering:** core domain and order lifecycle.
- **Catalog:** product identity, status, and current price.
- **Inventory:** stock quantities and reservations.
- **Payment:** fake provider integration and payment/refund lifecycle.
- **Fulfillment:** shipment creation and delivery lifecycle.
- **Shared kernel (small):** identifiers, event envelope primitives, clock, and cross-cutting technical abstractions only.

## Layer responsibilities

- **Domain:** aggregates, entities, value objects, policies, domain events, domain exceptions, repository protocols where domain-oriented.
- **Application:** commands/queries, handlers, orchestration within one context, transaction boundary, ports, DTOs.
- **Infrastructure:** MongoDB mappings/repositories, broker adapters, fake payment adapter, Outbox/Inbox implementations.
- **Presentation:** HTTP schemas, dependency wiring, routing, authentication/authorization hooks, error mapping.

## Communication rules

- Synchronous calls stay within a context.
- Cross-context business progression uses versioned integration events.
- Read-only composition may use explicit application contracts if documented; no direct collection or aggregate access.
- Domain events are internal facts; integration events are durable external contracts produced through the Outbox.

## Runtime components

- FastAPI API process.
- Outbox publisher worker.
- RabbitMQ consumer worker(s).
- MongoDB.
- RabbitMQ.
- Redis is excluded from version 1 and may be added only through an accepted ADR backed by a concrete need.

RabbitMQ handlers run as direct asynchronous consumers; Celery is not used.

## Consistency

Aggregate writes are strongly consistent within their own transaction boundary. The end-to-end workflow is eventually consistent. Failures are handled through retries, idempotency, and compensating events such as inventory release and payment refund.
