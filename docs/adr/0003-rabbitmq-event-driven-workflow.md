# ADR-0003: Use RabbitMQ for Cross-Context Workflows

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Order fulfillment must demonstrate asynchronous progression, retries, duplicate handling, and eventual consistency without Kafka's operational scope.

## Decision

Use RabbitMQ for integration events. Assume at-least-once delivery. Consumers are idempotent and use durable processed-message state. Do not use FastAPI background tasks for essential workflow steps.

## Consequences

The workflow remains available when publishing is temporarily unavailable, but clients observe intermediate states. Use direct asynchronous consumers and bounded exponential-backoff retries. Concrete exchange/queue names, retry delays, attempt limits, and dead-letter bindings are validated configuration rather than unresolved domain decisions.
