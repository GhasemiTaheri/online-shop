# Bounded Contexts

| Context | Classification | Owns | Publishes | Consumes |
|---|---|---|---|---|
| Ordering | Core | Order | OrderPlaced, OrderCancelled, OrderConfirmed | InventoryReserved/Rejected, PaymentAuthorized/Failed/Refunded, ShipmentShipped/Delivered |
| Catalog | Supporting | Product | ProductCreated/PriceChanged/Deactivated (optional v1) | None required |
| Inventory | Supporting | InventoryItem, InventoryReservation | InventoryReserved/Rejected/Released/ReservationCommitted | OrderPlaced, OrderCancelled, PaymentFailed |
| Payment | Generic | Payment | PaymentAuthorized/Failed/Refunded | InventoryReserved, OrderCancelled |
| Fulfillment | Supporting | Shipment | ShipmentCreated/Shipped/Delivered | OrderConfirmed |

## Context map

```text
Catalog --product snapshot contract--> Ordering
Ordering --OrderPlaced-------------> Inventory
Inventory --Reserved/Rejected------> Ordering, Payment
Payment --Authorized/Failed--------> Ordering, Inventory
Ordering --OrderConfirmed----------> Fulfillment
Fulfillment --Shipped/Delivered----> Ordering
```

## Boundary constraints

- Ordering stores a snapshot and does not reference a live Product object after placement.
- Inventory reasons about product IDs and quantities, not Order aggregates.
- Payment accepts an order ID, amount, currency, and opaque test token through a contract.
- Fulfillment receives the shipping-address snapshot with the confirmation event.
- No module imports another module's `domain` or `infrastructure` packages.
- Cross-context event payloads are owned contracts, not serialized domain objects.

## Candidate package shape

```text
src/online_shop/
  shared/
  catalog/{domain,application,infrastructure,presentation}/
  ordering/{domain,application,infrastructure,presentation}/
  inventory/{domain,application,infrastructure,presentation}/
  payment/{domain,application,infrastructure,presentation}/
  fulfillment/{domain,application,infrastructure,presentation}/
  main.py
```

Create directories when a slice becomes real; do not pre-create dozens of empty files.
