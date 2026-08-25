# API Overview

## Conventions

- Base path: `/api/v1`.
- JSON request/response bodies; UTF-8.
- IDs are opaque strings (UUID recommended).
- Timestamps use ISO 8601 UTC.
- Money is represented as a decimal string plus ISO currency code.
- Requests propagate `X-Correlation-ID`; the server creates one when absent and echoes it in every successfully completed request response.
- `POST /orders` requires `Idempotency-Key`.
- List endpoints use cursor pagination with a default page size of 20 and maximum of 100.
- Version 1 accepts only EUR monetary values.
- Customer identity is a trusted request value; there is no customer authentication in version 1.
- Admin endpoints require `X-Admin-Key`; development payment-control endpoints are registered only in development/test.

## Asynchronous commands

Order creation returns the persisted order immediately; downstream inventory/payment/fulfillment completes asynchronously. Clients observe progress by retrieving the order. A dedicated timeline endpoint is optional and should not be added without a requirement.

After the Order and `OrderPlaced` Outbox record are durably persisted, order creation returns `201 Created`, includes `Location: /api/v1/orders/{order_id}`, and returns the current asynchronous workflow status. A replay with the same idempotency key and identical request returns the stored original response; a different request with the same active key returns `409 Conflict`.

## Error shape

```json
{
  "error": {
    "code": "ORDER_NOT_CANCELLABLE",
    "message": "The order cannot be cancelled in its current state.",
    "details": {}
  }
}
```

## HTTP error mapping

Every error uses the documented envelope and a stable machine-readable `code`.

Expected failures are defined by their owning bounded context. For example,
Ordering uses `OrderingException` with `DomainException`, `ConflictException`,
`NotFoundException`, and `InfraException` subclasses. Each route catches the
exceptions propagated by its use case and maps them to the documented response;
the exceptions themselves do not depend on FastAPI.

| Status | Use |
|---:|---|
| `400 Bad Request` | Malformed JSON, malformed headers/cursors, or a request that cannot be parsed |
| `401 Unauthorized` | Missing or invalid `X-Admin-Key` on an admin endpoint |
| `404 Not Found` | Requested product, order, inventory item, payment, or shipment does not exist |
| `409 Conflict` | Idempotency-key payload mismatch, invalid state transition, optimistic-concurrency conflict, duplicate unique value, insufficient stock, or an adjustment below reserved stock |
| `422 Unprocessable Content` | Well-formed request whose field/domain values are invalid, such as empty items, non-positive quantity, unsupported currency, or invalid address |
| `500 Internal Server Error` | Unexpected non-retryable server defect; return no internal detail |
| `503 Service Unavailable` | Required dependency unavailable/readiness failure or a transient failure that cannot be accepted safely |

FastAPI's default validation response must be mapped into the project's standard error envelope. Do not use `403` for an invalid admin key because no authenticated principal exists in version 1.
