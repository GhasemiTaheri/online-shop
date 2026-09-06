from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from catalog.application.product_snapshots import CatalogProductSnapshotReader
from catalog.application.create_product import create_product
from catalog.domain.commands import CreateProduct
from catalog.domain.product import Currency, Money, Product, ProductId
from catalog.domain.repository import ProductRepositoryAbs


class Products(ProductRepositoryAbs):
    def __init__(self, products) -> None:
        self.products = products

    async def add(self, product) -> None:
        self.products[product.id] = product

    async def get_many(self, product_ids):
        return {product_id: self.products[product_id] for product_id in product_ids if product_id in self.products}


@pytest.mark.asyncio
async def test_catalog_snapshot_is_data_only_and_includes_active_state() -> None:
    product_id = uuid4()
    product = Product(ProductId(product_id), "A" * 20, "T-Shirt", None,
                      Money(Decimal("19.95"), Currency.EUR), False, 1,
                      datetime.now(UTC), datetime.now(UTC))

    snapshots = await CatalogProductSnapshotReader(Products({product_id: product})).get_many((product_id,))

    assert snapshots[product_id].name == "T-Shirt"
    assert snapshots[product_id].unit_price == Decimal("19.95")
    assert not snapshots[product_id].active


@pytest.mark.asyncio
async def test_create_product_uses_a_eur_price_and_a_twenty_character_sku() -> None:
    products = Products({})
    product = await create_product(CreateProduct(name="T-Shirt", price=Decimal("19.95")), products)

    assert product.price.currency is Currency.EUR
    assert len(product.sku) == 20
    assert product.sku.isascii() and product.sku.isalpha()
