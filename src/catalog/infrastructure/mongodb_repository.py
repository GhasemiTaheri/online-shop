"""Mongo persistence adapter for Catalog products."""

from typing import Any
from uuid import UUID

from pymongo.asynchronous.collection import AsyncCollection

from catalog.domain.product import Currency, Money, Product, ProductId
from catalog.domain.repository import ProductRepositoryAbs


class MongoProductRepository(ProductRepositoryAbs):
    def __init__(self, collection: AsyncCollection) -> None:
        self._collection = collection

    async def add(self, product: Product) -> None:
        await self._collection.insert_one(_to_document(product))

    async def get_many(self, product_ids: tuple[UUID, ...]) -> dict[UUID, Product]:
        cursor = self._collection.find({"_id": {"$in": [str(value) for value in product_ids]}})
        products = [_from_document(document) async for document in cursor]
        return {product.id: product for product in products}


def _to_document(product: Product) -> dict[str, Any]:
    return {"_id": str(product.id), "sku": product.sku, "name": product.name,
            "description": product.description, "price": {"amount": str(product.price.amount), "currency": product.price.currency.value},
            "active": product.active, "version": product.version,
            "created_at": product.created_at, "updated_at": product.updated_at}


def _from_document(document: dict[str, Any]) -> Product:
    from decimal import Decimal
    return Product(ProductId(UUID(document["_id"])), document["sku"], document["name"], document.get("description"),
                   Money(Decimal(document["price"]["amount"]), Currency(document["price"]["currency"])), document["active"],
                   document["version"], document["created_at"], document["updated_at"])
