import pytest

from ordering.application.messagebus import MessageBus


class CreateThing:
    pass


@pytest.mark.asyncio
async def test_message_bus_dispatches_and_returns_handler_result() -> None:
    async def handle_create(message: CreateThing) -> str:
        assert isinstance(message, CreateThing)
        return "created"

    result = await MessageBus({CreateThing: handle_create}).handle(CreateThing())

    assert result == "created"


@pytest.mark.asyncio
async def test_message_bus_propagates_handler_failures() -> None:
    async def failing_handler(message: CreateThing) -> None:
        raise RuntimeError("failure")

    with pytest.raises(RuntimeError, match="failure"):
        await MessageBus({CreateThing: failing_handler}).handle(CreateThing())


@pytest.mark.asyncio
async def test_message_bus_rejects_unregistered_messages() -> None:
    with pytest.raises(ValueError, match="No command handler"):
        await MessageBus({}).handle(CreateThing())
