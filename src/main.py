from fastapi import FastAPI
from settings import load_settings

settings = load_settings()
app = FastAPI()


@app.get("/hello-world")
async def hello_world() -> dict[str, str]:
    """Return a minimal response for local health checks."""
    return {"message": "Hi", "status": settings.mongodb.uri}
