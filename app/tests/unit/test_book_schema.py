from urllib.parse import quote

from app.core.config import settings
from app.schemas.book import BookOut


def make_book_out(cover_url: str | None) -> BookOut:
    return BookOut(
        isbn="0451524934",
        title="Nineteen Eighty-Four",
        authors=["George Orwell"],
        cover_url=cover_url,
    )


def test_cover_url_gets_proxied():
    book = make_book_out("https://covers.openlibrary.org/b/id/12054527-M.jpg")

    expected = f"{settings.public_base_url}/catalog/covers?src=" + quote(
        "https://covers.openlibrary.org/b/id/12054527-M.jpg", safe=""
    )
    assert book.cover_url == expected


def test_none_cover_url_stays_none():
    book = make_book_out(None)

    assert book.cover_url is None
