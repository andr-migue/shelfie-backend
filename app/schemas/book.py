from pydantic import BaseModel


class BookOut(BaseModel):
    isbn: str
    title: str
    authors: list[str]
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None
