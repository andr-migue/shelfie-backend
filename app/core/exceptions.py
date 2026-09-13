import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse


class BookNotFoundError(Exception):
    pass


class BookInUseError(Exception):
    pass


class BookNotFoundInCatalogError(Exception):
    pass


class DuplicateLibraryEntryError(Exception):
    pass


class LibraryEntryNotFoundError(Exception):
    pass


class CoverHostNotAllowedError(Exception):
    pass


class CoverNotFoundError(Exception):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookNotFoundError)
    async def book_not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Book not found"})

    @app.exception_handler(BookInUseError)
    async def book_in_use_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": "Book is referenced by a library entry"})

    @app.exception_handler(BookNotFoundInCatalogError)
    async def book_not_found_in_catalog_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Book not found in Open Library"})

    @app.exception_handler(DuplicateLibraryEntryError)
    async def duplicate_library_entry_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": "This book is already in your library"})

    @app.exception_handler(LibraryEntryNotFoundError)
    async def library_entry_not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Library entry not found"})

    @app.exception_handler(httpx.TransportError)
    async def open_library_unreachable_handler(request, exc):
        return JSONResponse(status_code=502, content={"detail": "Could not reach Open Library"})

    @app.exception_handler(CoverHostNotAllowedError)
    async def cover_host_not_allowed_handler(request, exc):
        return JSONResponse(status_code=400, content={"detail": "Cover host not allowed"})

    @app.exception_handler(CoverNotFoundError)
    async def cover_not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": "Cover not found"})
