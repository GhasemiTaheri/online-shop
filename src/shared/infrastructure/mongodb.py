"""MongoDB client construction for application processes."""

from pymongo import AsyncMongoClient

from settings import MongoDBSettings


def create_mongo_client(settings: MongoDBSettings) -> AsyncMongoClient:
    """Create the process-local asynchronous MongoDB client.

    Callers own the client lifecycle and must close it during process shutdown.
    """

    return AsyncMongoClient(settings.uri)
