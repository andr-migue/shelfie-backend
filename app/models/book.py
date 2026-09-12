from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed


class Book(Document):
    isbn: Annotated[str, Indexed(unique=True)]
    title: str
    authors: list[str]
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None
    source: str = "open_library"
    fetched_at: datetime

    class Settings:
        name = "books"
