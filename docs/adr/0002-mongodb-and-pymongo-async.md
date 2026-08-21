# ADR-0002: Use MongoDB with PyMongo Async

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

The domain contains aggregate-shaped data and variable event documents. The project needs persistence that does not leak ODM models into the domain.

## Decision

Use MongoDB through the PyMongo asynchronous API and explicit domain/document mappers. Repository implementations live in infrastructure. Prefer document/aggregate modeling over broad transactions.

## Consequences

Mapping code is explicit and testable, with less ODM convenience. Transactional Outbox support requires a replica-set configuration. One MongoDB deployment hosts a separate logical database for each bounded context.
