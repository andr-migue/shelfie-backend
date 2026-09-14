from datetime import datetime
from urllib.parse import quote

from pydantic import BaseModel, field_validator

from app.core.config import settings


class BookOut(BaseModel):
    isbn: str
    title: str
    authors: list[str]
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None

    @field_validator("cover_url")
    @classmethod
    def proxy_cover_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return f"{settings.public_base_url}/catalog/covers?src={quote(value, safe='')}"


class BookCreate(BaseModel):
    isbn: str
    title: str
    authors: list[str]
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None
    source: str
    fetched_at: datetime


class BookUpdate(BaseModel):
    title: str | None = None
    authors: list[str] | None = None
    cover_url: str | None = None
    publisher: str | None = None
    published_year: int | None = None
    page_count: int | None = None
