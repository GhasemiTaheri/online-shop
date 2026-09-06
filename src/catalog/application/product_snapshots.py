"""Catalog's documented read contract for Ordering."""

from uuid import UUID

from catalog.domain.repository import ProductRepositoryAbs
from ordering.application.product_snapshots import ProductSnapshot


class CatalogProductSnapshotReader:
    """Adapt Catalog products to Ordering's data-only snapshot port."""

    def __init__(self, products: ProductRepositoryAbs) -> None:
        self._products = products

    async def get_many(self, product_ids: tuple[UUID, ...]) -> dict[UUID, ProductSnapshot]:
        products = await self._products.get_many(product_ids)
        return {
            product_id: ProductSnapshot(
                product_id=product.id, name=product.name,
                unit_price=product.price.amount, currency=product.price.currency.value,
                active=product.active,
            )
            for product_id, product in products.items()
        }
