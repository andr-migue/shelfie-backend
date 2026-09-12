from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.db import init_db
from app.core.exceptions import BookInUseError, BookNotFoundError
from app.routers import books as books_router


@asynccontextmanager
async def lifespan(app):
    mongo_client = await init_db()

    app.state.http_client = httpx.AsyncClient(
        base_url=settings.open_library_base_url,
        timeout=settings.http_timeout
    )

    yield

    await app.state.http_client.aclose()
    await mongo_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(books_router.router)


@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404, content={"detail": "Book not found"}
    )


@app.exception_handler(BookInUseError)
async def book_in_use_handler(request, exc):
    return JSONResponse(
        status_code=409, content={"detail": "Book is referenced by a library entry"}
    )
