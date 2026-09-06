"""MongoDB repository implementation for Ordering."""

from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.collection import AsyncCollection

from ordering.domain.repository import OrderRepositoryAbs
from ordering.domain.order import Order, OrderId
from ordering.infrastructure.mongodb_mapper import order_from_document, order_to_document


class MongoOrderRepository(OrderRepositoryAbs):
    """Store Ordering aggregates using the current MongoDB transaction session."""

    def __init__(
        self,
        collection: AsyncCollection,
        session: AsyncClientSession | None = None,
    ) -> None:
        self._collection = collection
        self._session_provider = session

    async def add(self, order: Order) -> None:
        await self._collection.insert_one(
            order_to_document(order), session=self._session_provider
        )

    async def get(self, order_id: OrderId) -> Order | None:
        document = await self._collection.find_one(
            {"_id": str(order_id)}, session=self._session_provider
        )
        return None if document is None else order_from_document(document)
