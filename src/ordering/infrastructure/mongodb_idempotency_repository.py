"""MongoDB-backed idempotency records for Ordering."""

from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.collection import AsyncCollection

from ordering.domain.idempotency import IdempotencyRecord
from ordering.domain.order import CustomerId, OrderId
from ordering.domain.repository import IdempotencyRepositoryAbs


class MongoIdempotencyRepository(IdempotencyRepositoryAbs):
    """Store idempotency results inside the same Ordering transaction."""

    def __init__(
        self,
        collection: AsyncCollection,
        session_provider: Callable[[], AsyncClientSession],
    ) -> None:
        self._collection = collection
        self._session_provider = session_provider

    async def deactivate_expired(
        self, customer_id: CustomerId, route: str, key: str, now: datetime
    ) -> None:
        await self._collection.update_many(
            {
                "customer_id": str(customer_id),
                "route": route,
                "key": key,
                "active": True,
                "expires_at": {"$lte": now},
            },
            {"$set": {"active": False}},
            session=self._session_provider(),
        )

    async def get_active(
        self, customer_id: CustomerId, route: str, key: str, now: datetime
    ) -> IdempotencyRecord | None:
        document = await self._collection.find_one(
            {
                "customer_id": str(customer_id),
                "route": route,
                "key": key,
                "active": True,
                "expires_at": {"$gt": now},
            },
            session=self._session_provider(),
        )
        return None if document is None else _from_document(document)

    async def add(self, record: IdempotencyRecord) -> None:
        await self._collection.insert_one(
            {
                "customer_id": str(record.customer_id),
                "route": record.route,
                "key": record.key,
                "request_fingerprint": record.request_fingerprint,
                "order_id": str(record.order_id),
                "expires_at": record.expires_at,
                "active": record.active,
            },
            session=self._session_provider(),
        )


def _from_document(document: dict) -> IdempotencyRecord:
    return IdempotencyRecord(
        customer_id=CustomerId(UUID(document["customer_id"])),
        route=document["route"],
        key=document["key"],
        request_fingerprint=document["request_fingerprint"],
        order_id=OrderId(UUID(document["order_id"])),
        expires_at=document["expires_at"],
        active=document["active"],
    )
