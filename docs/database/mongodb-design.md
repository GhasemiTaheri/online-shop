# MongoDB Design

## Ownership

Use one MongoDB deployment with a separate logical database per bounded context. Each context owns its collections and mapping code; no context reads another context's database or collections directly.

## Candidate collections

| Context | Collections |
|---|---|
| Catalog | `products`, `outbox` |
| Ordering | `orders`, `idempotency_keys`, `inbox`, `outbox` |
| Inventory | `inventory_items`, `reservations` if separate, `inbox`, `outbox` |
| Payment | `payments`, `inbox`, `outbox` |
| Fulfillment | `shipments`, `inbox`, `outbox` |

## Document guidance

- Embed order-line and address snapshots in Order because they belong to its consistency boundary.
- Do not embed unbounded event histories in aggregates; use logs/outbox or a dedicated timeline read model only if required.
- Persist a numeric `version` on concurrency-sensitive aggregates.
- Store Decimal128 or integer minor units consistently; mapping must preserve domain `Decimal` semantics.
- Store UTC BSON datetimes and normalize at boundaries.
- Keep persistence field names/schema separate from domain implementation through explicit mappers.

## Optimistic update

Match on aggregate ID and expected version, apply the update, and increment version. A zero-document match is a concurrency conflict; it is never treated as a successful no-op.

## Required indexes

- `products.sku`: unique and never reused; inactive product records are retained.
- `orders.customer_id + orders.created_at`: supports history pagination.
- `payments.order_id`: unique.
- `shipments.order_id`: unique.
- `inventory_items.product_id`: unique (often `_id`).
- `idempotency_keys.customer_id + route + key`: partial unique index where `active = true`, enforcing uniqueness during the 24-hour window while allowing a later key reuse. Do not use a MongoDB TTL index; retain expired records with `active = false` and an expiry timestamp.
- `inbox.consumer + event_id`: unique.
- `outbox.status + next_attempt_at + occurred_at`: publisher polling.
- `reservations.status + expires_at`: expiration-worker scan; this is a normal index, never a deletion TTL index.

## Outbox record

Store envelope, status, attempt count, next attempt time, last error summary, created/published timestamps, and a lock/lease if multiple publishers run. Never log or persist secrets in errors.

## Retention

Do not physically delete application records in version 1. Orders, products, reservations, payments, shipments, idempotency records, Inbox records, Outbox records, and failed operational records remain stored. Expiration is represented by state and timestamps. Any future archival or deletion policy requires a new explicit decision and migration plan.

## Transactions

Local MongoDB must run as a replica set if transactions are used. Aggregate write and related outbox insert share a local transaction. Cross-context transactions remain prohibited.
