from pydantic import BaseModel


class BookOut(BaseModel):
    isbn: str
    title: str
    authors: list[str]
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None

class BookUpdate(BaseModel):
    title: str | None = None
    authors: list[str] | None = None
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None