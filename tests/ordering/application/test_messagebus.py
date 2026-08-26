import pytest

from ordering.application.messagebus import MessageBus
from ordering.application.uow import OrderingUowAbs


class RecordingUow(OrderingUowAbs):
    def __init__(self) -> None:
        self.entered = False
        self.exited = False
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> "RecordingUow":
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        self.exited = True
        if not self.committed:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class CreateThing:
    pass


@pytest.mark.asyncio
async def test_message_bus_dispatches_within_uow_and_returns_handler_result() -> None:
    uow = RecordingUow()

    async def handle_create(message: CreateThing) -> str:
        assert isinstance(message, CreateThing)
        await uow.commit()
        return "created"

    result = await MessageBus(uow, {CreateThing: handle_create}).handle(CreateThing())

    assert result == "created"
    assert uow.entered
    assert uow.exited
    assert uow.committed
    assert not uow.rolled_back


@pytest.mark.asyncio
async def test_message_bus_rolls_back_when_handler_fails() -> None:
    uow = RecordingUow()

    async def failing_handler(message: CreateThing) -> None:
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError, match="failure"):
        await MessageBus(uow, {CreateThing: failing_handler}).handle(CreateThing())

    assert uow.entered
    assert uow.exited
    assert uow.rolled_back


@pytest.mark.asyncio
async def test_message_bus_rejects_unregistered_messages() -> None:
    uow = RecordingUow()

    with pytest.raises(ValueError, match="No command handler"):
        await MessageBus(uow, {}).handle(CreateThing())

    assert not uow.entered
