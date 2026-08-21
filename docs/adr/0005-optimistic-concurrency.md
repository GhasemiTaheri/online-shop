# ADR-0005: Use Optimistic Concurrency

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Concurrent inventory reservations can oversell stock, and competing order commands can overwrite lifecycle changes.

## Decision

Persist an integer version on Order and InventoryItem. Repositories update by ID plus expected version and atomically increment the version. A mismatch raises a typed concurrency conflict. Retry only explicitly safe/idempotent application commands.

## Consequences

No long-lived locks are required, but handlers need reload/retry or conflict behavior and concurrency tests. A multi-item reservation uses one per-order reservation record, deterministic item processing, and idempotent compensation when partial work fails.
