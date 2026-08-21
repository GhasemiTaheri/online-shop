# ADR-0001: Start with a Modular Monolith

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

The project must demonstrate DDD and reliable workflows within a 10–14 day portfolio scope. Starting with several deployed services would shift effort toward operations and distributed failure handling before the domain is mature.

## Decision

Build one deployable FastAPI codebase with strict bounded-context modules. API and worker processes may run separately. Cross-context contracts must be explicit so Inventory can be extracted later without redesigning Ordering.

## Consequences

Delivery and testing are simpler, while module boundaries still require discipline. Independent deployment/scaling is deferred. Inventory extraction is a stretch goal after the complete monolith works.
