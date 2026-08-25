"""PyMongo transaction boundary for the Ordering bounded context."""

from types import TracebackType
from typing import Self

from pymongo import AsyncMongoClient
from pymongo.asynchronous.client_session import AsyncClientSession

from ordering.application.repository import IdempotencyRepositoryAbs, OrderRepositoryAbs
from ordering.application.uow import OrderingUowAbs
from ordering.infrastructure.mongodb_idempotency_repository import (
    MongoIdempotencyRepository,
)
from ordering.infrastructure.mongodb_repository import MongoOrderRepository


class OrderingMongoUow(OrderingUowAbs):
    """Manage one local Ordering MongoDB transaction.

    The application process owns the injected client and closes it at shutdown.
    """

    def __init__(self, client: AsyncMongoClient, database_name: str) -> None:
        self._client = client
        self._session: AsyncClientSession | None = None
        self._finished = False
        database = client.get_database(database_name)
        self.orders: OrderRepositoryAbs = MongoOrderRepository(
            database.get_collection("orders"), self._active_session
        )
        self.idempotency: IdempotencyRepositoryAbs = MongoIdempotencyRepository(
            database.get_collection("idempotency_keys"), self._active_session
        )

    async def __aenter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("This unit of work is already active.")

        session = await self._client.start_session()
        try:
            session.start_transaction()
        except BaseException:
            await session.end_session()
            raise

        self._session = session
        self._finished = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return

        try:
            if not self._finished:
                await self.rollback()
        finally:
            await self._session.end_session()
            self._session = None

    async def commit(self) -> None:
        session = self._active_session()
        if self._finished:
            raise RuntimeError("This unit of work has already finished.")

        await session.commit_transaction()
        self._finished = True

    async def rollback(self) -> None:
        session = self._active_session()
        if self._finished:
            return

        await session.abort_transaction()
        self._finished = True

    def _active_session(self) -> AsyncClientSession:
        if self._session is None:
            raise RuntimeError("This unit of work has not been entered.")
        return self._session
