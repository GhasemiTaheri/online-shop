from pymongo import ASCENDING, AsyncMongoClient


async def ensure_catalog_indexes(client: AsyncMongoClient, database_name: str) -> None:
    await client.get_database(database_name).get_collection("products").create_index(
        [("sku", ASCENDING)], unique=True
    )
