import asyncio
import httpx

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .routes import router
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.hn_base_url,
        timeout=10.0,
    )
    yield
    await app.state.http_client.aclose()

app = FastAPI(title='HN Aggregator API', lifespan=lifespan)

app.include_router(router)