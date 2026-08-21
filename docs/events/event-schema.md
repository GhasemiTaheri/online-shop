# Integration Event Schema

## Envelope

```json
{
  "event_id": "uuid",
  "event_type": "InventoryReserved",
  "event_version": 1,
  "occurred_at": "2026-08-09T12:00:00Z",
  "correlation_id": "uuid-or-client-value",
  "causation_id": "event-or-command-id",
  "producer": "inventory",
  "payload": {}
}
```

## Field constraints

- `event_id`: globally unique immutable UUID.
- `event_type`: registered event name from the catalog.
- `event_version`: positive integer schema version.
- `occurred_at`: timezone-aware UTC timestamp set when the fact occurs.
- `correlation_id`: stable across one end-to-end business workflow.
- `causation_id`: identifier of the command/event that directly caused this event.
- `producer`: bounded-context name.
- `payload`: versioned event-specific object.

## Delivery contract

Delivery is at least once through direct asynchronous RabbitMQ consumers. Consumers acknowledge only after business changes and Inbox state are durable. Handlers tolerate redelivery and do not rely on global ordering. Outbox delivery uses exponential backoff with a configurable bounded attempt count; exhausted records become inspectable failures and emit a metric. Concrete exchange/queue names remain an implementation detail documented with the broker configuration.

Additive fields may be introduced without incrementing the version, and consumers must ignore unknown additive fields. Breaking schema changes increment `event_version`.
