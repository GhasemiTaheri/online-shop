from pymongo import ASCENDING, AsyncMongoClient


async def ensure_inventory_indexes(client: AsyncMongoClient, database_name: str) -> None:
    database = client.get_database(database_name)
    await database.get_collection("inventory_items").create_index([("_id", ASCENDING)], unique=True)
    await database.get_collection("reservations").create_index([("order_id", ASCENDING)], unique=True)
