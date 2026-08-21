# API Endpoints

## Catalog

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/products` | List active products |
| GET | `/api/v1/products/{product_id}` | Get product details |
| POST | `/api/v1/products` | Create product (admin) |
| PATCH | `/api/v1/products/{product_id}` | Change supported product fields (admin) |

## Inventory

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/inventory/{product_id}` | Get stock summary |
| POST | `/api/v1/inventory/{product_id}/adjustments` | Apply signed stock adjustment (admin) |

Reservation endpoints are internal workflow handlers, not public HTTP CRUD.

## Orders

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/orders` | Create an order; requires `Idempotency-Key`; returns `201 Created` |
| GET | `/api/v1/orders/{order_id}` | Get order and current status |
| GET | `/api/v1/orders?customer_id=...&cursor=...&limit=20` | List a customer's orders; limit is 1–100 |
| POST | `/api/v1/orders/{order_id}/cancel` | Cancel an eligible order with a reason |

Create request fields: `customer_id`, non-empty `items[{product_id, quantity}]`, `shipping_address`, and opaque `payment_method` test token. The response includes order ID, status, lines, total, and timestamps; never echo the payment token.

## Payments

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/payments/{payment_id}` | Diagnostic payment status |
| POST | `/api/v1/dev/payments/{payment_id}/approve` | Deterministic dev/test approval |
| POST | `/api/v1/dev/payments/{payment_id}/fail` | Deterministic dev/test failure |

Development endpoints must not be registered outside development/test. Admin catalog, inventory, shipment, and development-payment mutations require `X-Admin-Key`.

## Fulfillment

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/shipments/{shipment_id}` | Get shipment |
| POST | `/api/v1/shipments/{shipment_id}/ship` | Mark shipment shipped (admin/system) |
| POST | `/api/v1/shipments/{shipment_id}/deliver` | Mark shipment delivered (admin/system) |

Shipment transitions are manual admin actions only. Version 1 does not expose a carrier webhook.

## Operations

| Method | Path | Purpose |
|---|---|---|
| GET | `/health/live` | Process liveness |
| GET | `/health/ready` | Required dependency readiness |
| GET | `/metrics` | Prometheus-format metrics |
