from contextlib import asynccontextmanager

from fastapi import FastAPI

from catalog.application.product_snapshots import CatalogProductSnapshotReader
from catalog.infrastructure.mongodb_indexes import ensure_catalog_indexes
from catalog.infrastructure.mongodb_repository import MongoProductRepository
from ordering.infrastructure.mongodb_indexes import ensure_ordering_indexes
from ordering.presentation.orders import router as orders_router
from settings import load_settings
from shared.infrastructure.mongodb import create_mongo_client
from shared.observability.logging import configure_logging
from shared.presentation.middleware import install_correlation_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create one MongoDB client for this API process and close it on shutdown."""

    settings = load_settings()
    configure_logging(settings.app.log_level)
    app.state.settings = settings
    app.state.mongo_client = create_mongo_client(settings.mongodb)
    catalog_database = app.state.mongo_client.get_database(settings.mongodb.catalog_database)
    app.state.ordering_product_snapshots = CatalogProductSnapshotReader(
        MongoProductRepository(catalog_database.get_collection("products"))
    )
    await ensure_catalog_indexes(app.state.mongo_client, settings.mongodb.catalog_database)
    await ensure_ordering_indexes(
        app.state.mongo_client, settings.mongodb.ordering_database
    )
    try:
        yield
    finally:
        await app.state.mongo_client.close()


app = FastAPI(lifespan=lifespan)
install_correlation_middleware(app)
app.include_router(orders_router)


@app.get("/hello-world")
async def hello_world() -> dict[str, str]:
    """Return a minimal response for local health checks."""
    return {"message": "Hi", "status": "healthy"}
