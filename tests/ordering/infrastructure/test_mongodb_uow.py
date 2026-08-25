from __future__ import annotations

from typing import cast

import pytest
from pymongo import AsyncMongoClient

from ordering.infrastructure.mongodb_uow import OrderingMongoUow


class FakeSession:
    def __init__(self) -> None:
        self.started = False
        self.committed = False
        self.aborted = False
        self.ended = False

    def start_transaction(self) -> None:
        self.started = True

    async def commit_transaction(self) -> None:
        self.committed = True

    async def abort_transaction(self) -> None:
        self.aborted = True

    async def end_session(self) -> None:
        self.ended = True


class FakeClient:
    def __init__(self, session: FakeSession) -> None:
        self.session = session
        self.start_session_calls = 0

    async def start_session(self) -> FakeSession:
        self.start_session_calls += 1
        return self.session


@pytest.mark.asyncio
async def test_commit_commits_and_ends_the_session() -> None:
    session = FakeSession()
    uow = OrderingMongoUow(cast(AsyncMongoClient, FakeClient(session)))

    async with uow:
        await uow.commit()

    assert session.started
    assert session.committed
    assert not session.aborted
    assert session.ended


@pytest.mark.asyncio
async def test_uncommitted_exit_aborts_and_ends_the_session() -> None:
    session = FakeSession()
    uow = OrderingMongoUow(cast(AsyncMongoClient, FakeClient(session)))

    async with uow:
        pass

    assert session.started
    assert not session.committed
    assert session.aborted
    assert session.ended


@pytest.mark.asyncio
async def test_exception_aborts_and_preserves_the_exception() -> None:
    session = FakeSession()
    uow = OrderingMongoUow(cast(AsyncMongoClient, FakeClient(session)))

    with pytest.raises(ValueError, match="failure"):
        async with uow:
            raise ValueError("failure")

    assert session.aborted
    assert session.ended
