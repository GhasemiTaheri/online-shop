from abc import ABC, abstractmethod
from uuid import UUID

from catalog.domain.product import Product


class ProductRepositoryAbs(ABC):
    @abstractmethod
    async def add(self, product: Product) -> None: ...

    @abstractmethod
    async def get_many(self, product_ids: tuple[UUID, ...]) -> dict[UUID, Product]: ...
