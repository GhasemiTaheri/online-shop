"""Dependency providers for Ordering HTTP endpoints."""
import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from pymongo import AsyncMongoClient

from ordering.application import COMMAND_HANDLERS, messagebus

from ordering.infrastructure.mongodb_uow import OrderingMongoUow
from ordering.infrastructure.mongodb_repository import MongoOrderRepository


def get_order_repository(request: Request) -> MongoOrderRepository:
    client: AsyncMongoClient = request.app.state.mongo_client
    database_name: str = request.app.state.settings.mongodb.ordering_database
    return MongoOrderRepository(client.get_database(database_name).get_collection("orders"))


def get_ordering_messagebus(request: Request) -> messagebus.MessageBus:
    """Build the request-scoped dispatcher using the process Mongo client."""

    client: AsyncMongoClient = request.app.state.mongo_client
    database_name: str = request.app.state.settings.mongodb.ordering_database
    uow = OrderingMongoUow(client, database_name)
    dependencies = {"uow": uow, "product_snapshots": request.app.state.ordering_product_snapshots}
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(command_handlers=injected_command_handlers)


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
