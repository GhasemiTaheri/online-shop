"""MongoDB adapters for InventoryItem and Reservation."""

from typing import Any
from uuid import UUID

from pymongo import ReturnDocument
from pymongo.asynchronous.collection import AsyncCollection

from inventory.domain.inventory import InventoryItem, ProductId, Reservation, ReservationId, ReservationLine, ReservationStatus, OrderId
from inventory.domain.repository import InventoryItemRepositoryAbs, ReservationRepositoryAbs


class MongoInventoryItemRepository(InventoryItemRepositoryAbs):
    def __init__(self, collection: AsyncCollection) -> None:
        self.collection = collection

    async def get_many(self, product_ids):
        cursor = self.collection.find({"_id": {"$in": [str(value) for value in product_ids]}})
        items = [_from_item(document) async for document in cursor]
        return {item.product_id: item for item in items}

    async def save(self, item: InventoryItem, expected_version: int) -> None:
        result = await self.collection.find_one_and_update(
            {"_id": str(item.product_id), "version": expected_version},
            {"$set": {"on_hand": item.on_hand, "reserved": item.reserved, "version": item.version}},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            raise RuntimeError("Inventory version conflict.")


class MongoReservationRepository(ReservationRepositoryAbs):
    def __init__(self, collection: AsyncCollection) -> None:
        self.collection = collection

    async def get_by_order(self, order_id: UUID):
        document = await self.collection.find_one({"order_id": str(order_id)})
        return None if document is None else _from_reservation(document)

    async def add(self, reservation: Reservation) -> None:
        await self.collection.insert_one(_to_reservation(reservation))


def _from_item(document: dict[str, Any]) -> InventoryItem:
    return InventoryItem(ProductId(UUID(document["_id"])), document["on_hand"], document["reserved"], document["version"])


def _to_reservation(value: Reservation) -> dict[str, Any]:
    return {"_id": str(value.id), "order_id": str(value.order_id),
            "items": [{"product_id": str(item.product_id), "quantity": item.quantity} for item in value.items],
            "created_at": value.created_at, "expires_at": value.expires_at, "status": value.status.value}


def _from_reservation(document: dict[str, Any]) -> Reservation:
    return Reservation(ReservationId(UUID(document["_id"])), OrderId(UUID(document["order_id"])),
                       tuple(ReservationLine(ProductId(UUID(item["product_id"])), item["quantity"]) for item in document["items"]),
                       document["created_at"], document["expires_at"], ReservationStatus(document["status"]))
