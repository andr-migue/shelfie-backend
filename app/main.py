from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.core.db import init_db
from app.core.exceptions import register_exception_handlers
from app.routers.router import router


@asynccontextmanager
async def lifespan(app):
    mongo_client = await init_db()

    app.state.open_library_http_client = httpx.AsyncClient(
        base_url=settings.open_library_base_url, 
        timeout=settings.http_timeout
    )

    yield

    await app.state.open_library_http_client.aclose()
    await mongo_client.close()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(router)
