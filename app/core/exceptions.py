from fastapi import FastAPI
from fastapi.responses import JSONResponse


class BookNotFoundError(Exception):
    pass


class BookInUseError(Exception):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookNotFoundError)
    async def book_not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Book not found"})

    @app.exception_handler(BookInUseError)
    async def book_in_use_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": "Book is referenced by a library entry"})
