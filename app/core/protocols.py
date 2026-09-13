from dataclasses import dataclass
from typing import Protocol


@dataclass
class BookMetadata:
    title: str
    authors: list[str]
    isbn: str
    cover_url: str | None
    publisher: str | None
    published_year: int | None
    page_count: int | None


class BookClient(Protocol):
    async def get_by_isbn(self, isbn: str) -> BookMetadata | None: ...
