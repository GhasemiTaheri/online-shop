# ADR-0006: Retain Records and Model Expiration as State

- **Status:** Accepted
- **Date:** 2026-08-22

## Context

The portfolio system needs inspectable audit history for orders, messaging, failures, and inventory reservations. A MongoDB TTL index would physically remove records and, for reservations, could remove evidence without safely releasing held inventory.

## Decision

Do not physically delete application records in version 1. Model expiration through explicit status and timestamps. A scheduled worker finds active reservations at or beyond `expires_at`, idempotently releases inventory, marks the reservation `EXPIRED`, and publishes the corresponding integration event. Idempotency records similarly become inactive after their 24-hour enforcement window but remain stored.

Retry only failures explicitly classified as transient, using bounded retry policies. Preserve exhausted failures in an inspectable state. When recovery semantics are unclear and affect business state or data, obtain a user/domain decision rather than inventing compensation or deletion behavior.

## Consequences

Audit and debugging evidence is retained and expiration has correct business behavior. Database size grows indefinitely in version 1, which is acceptable for the portfolio scope but not a production retention strategy. A future archive/delete policy requires a separate ADR and migration plan.
