"""Inventory reservation command handler."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from inventory.domain.inventory import OrderId, ProductId, Reservation, ReservationId, ReservationLine
from inventory.domain.repository import InventoryItemRepositoryAbs, ReservationRepositoryAbs


class InventoryConflictError(Exception):
    pass


class InventoryReservationError(Exception):
    pass


async def reserve_inventory(order_id: UUID, requested_items: tuple[tuple[UUID, int], ...],
                            items: InventoryItemRepositoryAbs, reservations: ReservationRepositoryAbs,
                            now: datetime | None = None) -> Reservation:
    existing = await reservations.get_by_order(order_id)
    if existing is not None:
        return existing
    now = now or datetime.now(UTC)
    ordered = tuple(sorted(requested_items, key=lambda value: str(value[0])))
    product_ids = tuple(ProductId(product_id) for product_id, _ in ordered)
    loaded = await items.get_many(product_ids)
    if len(loaded) != len(set(product_ids)):
        raise InventoryReservationError("An inventory item was not found.")
    changed: list[tuple[object, int]] = []
    try:
        for product_id, quantity in ordered:
            item = loaded[product_id]
            before = item.version
            item.reserve(quantity)
            await items.save(item, before)
            changed.append((item, quantity))
        reservation = Reservation(ReservationId(uuid4()), OrderId(order_id),
                                  tuple(ReservationLine(ProductId(pid), qty) for pid, qty in ordered),
                                  now, now + timedelta(hours=24))
        await reservations.add(reservation)
        return reservation
    except Exception as exc:
        for item, quantity in reversed(changed):
            item.release(quantity)
            try:
                await items.save(item, item.version - 1)
            except Exception:
                pass
        raise InventoryReservationError("Inventory could not be reserved.") from exc
