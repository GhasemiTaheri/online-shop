"""Dependency providers for Ordering HTTP endpoints."""
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from pymongo import AsyncMongoClient

from ordering.application import COMMAND_HANDLERS, messagebus

from ordering.infrastructure.mongodb_uow import OrderingMongoUow


def get_ordering_messagebus(request: Request) -> messagebus.MessageBus:
    """Build the request-scoped dispatcher using the process Mongo client."""

    client: AsyncMongoClient = request.app.state.mongo_client
    uow = OrderingMongoUow(client)
    dependencies = {"uow": uow}
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(
        handler: Callable[..., Awaitable[Any]], dependencies: dict[str, object]
) -> Callable[[object], Awaitable[Any]]:
    """Bind declared infrastructure dependencies to an application handler."""

    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
