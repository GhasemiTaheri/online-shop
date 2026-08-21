# ADR-0004: Publish Integration Events through a Transactional Outbox

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Writing an aggregate and publishing directly to RabbitMQ can lose an event if the process fails between those operations.

## Decision

Persist the aggregate change and outgoing integration event in one local MongoDB transaction. A separate publisher claims and publishes pending records, then records delivery state. Consumers remain idempotent because publishing can repeat.

## Consequences

This closes the database/broker dual-write gap but adds polling, leasing, retries, backlog monitoring, and cleanup concerns. It does not provide exactly-once delivery.
