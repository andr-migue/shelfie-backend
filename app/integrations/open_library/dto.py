from dataclasses import dataclass


@dataclass
class OpenLibrarySearchResult:
    title: str
    authors: list[str]
    isbn: str | None
    cover_id: int | None
    publisher: str | None
    published_year: int | None
    page_count: int | None


@dataclass
class OpenLibraryBookResult:
    title: str
    authors: list[str]
    isbn: str
    cover_url: str | None
    publisher: str | None
    published_year: int | None
    page_count: int | None
