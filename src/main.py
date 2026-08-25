from contextlib import asynccontextmanager

from fastapi import FastAPI

from ordering.presentation.orders import router as orders_router
from settings import load_settings
from shared.infrastructure.mongodb import create_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create one MongoDB client for this API process and close it on shutdown."""

    settings = load_settings()
    app.state.mongo_client = create_mongo_client(settings.mongodb)
    try:
        yield
    finally:
        await app.state.mongo_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(orders_router)


@app.get("/hello-world")
async def hello_world() -> dict[str, str]:
    """Return a minimal response for local health checks."""
    return {"message": "Hi", "status": "healthy"}
