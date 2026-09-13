from typing import Protocol

from app.integrations.open_library.dto import OpenLibraryBookResult


class BookClient(Protocol):
    async def get_by_isbn(self, isbn: str) -> OpenLibraryBookResult | None: ...
