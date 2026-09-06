"""Internal Catalog product creation command."""

from datetime import UTC, datetime
import secrets
import string
from uuid import uuid4

from catalog.domain.commands import CreateProduct
from catalog.domain.product import Currency, Money, Product, ProductId
from catalog.domain.repository import ProductRepositoryAbs


def generate_sku() -> str:
    return "".join(secrets.choice(string.ascii_letters) for _ in range(20))


async def create_product(command: CreateProduct, products: ProductRepositoryAbs) -> Product:
    now = datetime.now(UTC)
    product = Product(ProductId(uuid4()), generate_sku(), command.name, command.description,
                      Money(command.price, Currency.EUR), True, 1, now, now)
    await products.add(product)
    return product
