# Functional Requirements

## Catalog

- **FR-01:** Clients can list active products.
- **FR-02:** Clients can retrieve one product by ID.
- **FR-03:** An administrator can create a product.
- **FR-04:** An administrator can change a product price.
- **FR-05:** Inactive or missing products cannot be added to new orders.

## Inventory

- **FR-06:** An administrator can apply a signed stock adjustment with a reason.
- **FR-06A:** A stock reduction that would make on-hand quantity lower than reserved quantity is rejected atomically and changes nothing.
- **FR-07:** Inventory can reserve requested quantities for an order.
- **FR-08:** A reservation is rejected atomically when any requested item lacks stock.
- **FR-09:** A reservation can be released when an order is cancelled or payment fails.
- **FR-10:** Concurrent requests cannot oversell inventory.
- **FR-11:** A successful reservation can be committed after payment authorization.
- **FR-11A:** An uncommitted active reservation expires after 24 hours; expiration releases its stock idempotently while retaining the reservation record.

## Ordering

- **FR-12:** A customer can create an order containing one or more products.
- **FR-13:** Order creation requires an `Idempotency-Key`; replaying the same key and request returns the original result.
- **FR-14:** Reusing an idempotency key with a different request is rejected.
- **FR-15:** Product ID, name, unit price, and currency are snapshotted into each order line.
- **FR-16:** The Order aggregate calculates line subtotals and the total.
- **FR-17:** A client can retrieve an order by ID.
- **FR-18:** A client can list orders for one customer using cursor pagination, ordered newest-first by default, with a default page size of 20 and maximum of 100.
- **FR-19:** Orders follow only valid lifecycle transitions.
- **FR-20:** An order cannot be confirmed without inventory reservation and successful payment authorization.
- **FR-21:** A customer can cancel an eligible order with a reason.
- **FR-22:** Cancellation releases reserved inventory when applicable.
- **FR-23:** Cancellation initiates a refund when a payment has already been authorized and the cancellation policy permits it.
- **FR-24:** An order cannot be cancelled after its shipment is shipped.

## Payment

- **FR-25:** A payment is created only for an inventory-reserved order.
- **FR-26:** The fake payment gateway supports deterministic authorization success and failure.
- **FR-27:** Duplicate authorization requests cannot create duplicate charges.
- **FR-28:** An authorized payment can be refunded once.
- **FR-29:** Payment status can be retrieved for diagnostics.
- **FR-29A:** Successful authorization is the completed fake charge; there is no separate capture operation.

## Fulfillment

- **FR-30:** A shipment is created only after order confirmation.
- **FR-31:** Each shipment receives a unique tracking number.
- **FR-32:** A shipment can transition from created/ready to shipped.
- **FR-33:** A shipped shipment can transition to delivered.
- **FR-34:** Shipment state transitions update the corresponding order through events, not direct aggregate access.
- **FR-34A:** Shipment transitions are initiated manually through admin endpoints; version 1 has no carrier webhook.

## Messaging and operations

- **FR-35:** Domain changes can raise domain events.
- **FR-36:** Outgoing integration events are stored atomically with the originating aggregate change.
- **FR-37:** The publisher retries transient failures.
- **FR-38:** Consumers are idempotent and duplicate messages do not duplicate business operations.
- **FR-39:** Liveness and readiness endpoints report process and dependency status.
- **FR-40:** A metrics endpoint exposes operational measurements.
- **FR-41:** Application records are never physically deleted; expired and failed records remain inspectable.

## Accepted scope constraints

- Version 1 supports EUR only.
- Customer APIs accept a trusted `customer_id`; customer authentication and ownership enforcement are out of scope.
- Admin operations require the environment-provided `X-Admin-Key`.
- Idempotency keys are scoped by customer and route and enforce replay for 24 hours; expired records remain stored but no longer enforce replay.
- Redis is not part of version 1.

## Acceptance flow

The minimum demonstrable workflow is:

`OrderPlaced -> InventoryReserved -> PaymentAuthorized -> OrderConfirmed -> ShipmentCreated`

Required negative demonstrations are `InventoryRejected`, `PaymentFailed`, duplicate event delivery, concurrent reservation conflict/retry, and publisher retry.
