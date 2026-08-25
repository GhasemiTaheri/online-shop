"""MongoDB indexes required by the Ordering context."""

from pymongo import ASCENDING, DESCENDING, AsyncMongoClient


async def ensure_ordering_indexes(client: AsyncMongoClient, database_name: str) -> None:
    """Create durable query and idempotency constraints without TTL deletion."""

    database = client.get_database(database_name)
    await database.get_collection("orders").create_index(
        [("customer_id", ASCENDING), ("created_at", DESCENDING)]
    )
    await database.get_collection("idempotency_keys").create_index(
        [("customer_id", ASCENDING), ("route", ASCENDING), ("key", ASCENDING)],
        unique=True,
        partialFilterExpression={"active": True},
    )
