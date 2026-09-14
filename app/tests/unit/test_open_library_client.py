import httpx
import pytest

from app.integrations.open_library.client import OpenLibraryClient

ISBN = "0451524934"

OPEN_LIBRARY_RESPONSE = {
    f"ISBN:{ISBN}": {
        "title": "Nineteen Eighty-Four",
        "authors": [{"name": "George Orwell"}],
        "publishers": [{"name": "Signet Classics"}],
        "publish_date": "1993",
        "number_of_pages": 328,
        "cover": {"medium": "https://covers.openlibrary.org/b/id/12054527-M.jpg"},
    }
}


def make_client() -> OpenLibraryClient:
    http_client = httpx.AsyncClient(base_url="https://openlibrary.org", timeout=5.0)
    return OpenLibraryClient(http_client)


async def test_get_by_isbn_returns_parsed_book_when_found(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json=OPEN_LIBRARY_RESPONSE)
    )
    client = make_client()

    result = await client.get_by_isbn(ISBN)

    assert result is not None
    assert result.title == "Nineteen Eighty-Four"
    assert result.authors == ["George Orwell"]
    assert result.isbn == ISBN
    assert result.cover_url == "https://covers.openlibrary.org/b/id/12054527-M.jpg"
    assert result.publisher == "Signet Classics"
    assert result.published_year == 1993
    assert result.page_count == 328


async def test_get_by_isbn_returns_none_when_not_found(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        return_value=httpx.Response(200, json={})
    )
    client = make_client()

    result = await client.get_by_isbn(ISBN)

    assert result is None


async def test_get_by_isbn_propagates_timeout_when_open_library_is_down(respx_mock):
    respx_mock.get("https://openlibrary.org/api/books").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    client = make_client()

    with pytest.raises(httpx.TimeoutException):
        await client.get_by_isbn(ISBN)


async def test_search_builds_cover_url_from_cover_id(respx_mock):
    respx_mock.get("https://openlibrary.org/search.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "docs": [
                    {
                        "title": "Dune",
                        "author_name": ["Frank Herbert"],
                        "isbn": ["9780441172719"],
                        "cover_i": 11481354,
                        "publisher": ["Ace Books"],
                        "first_publish_year": 1965,
                        "number_of_pages_median": 412,
                    }
                ]
            },
        )
    )
    client = make_client()

    results = await client.search("dune")

    assert len(results) == 1
    assert results[0].isbn == "9780441172719"
    assert results[0].cover_url == "https://covers.openlibrary.org/b/id/11481354-M.jpg"


async def test_search_without_cover_id_leaves_cover_url_none(respx_mock):
    respx_mock.get("https://openlibrary.org/search.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "docs": [
                    {
                        "title": "Dune",
                        "author_name": ["Frank Herbert"],
                        "isbn": ["9780441172719"],
                    }
                ]
            },
        )
    )
    client = make_client()

    results = await client.search("dune")

    assert results[0].cover_url is None


async def test_search_skips_docs_without_isbn(respx_mock):
    respx_mock.get("https://openlibrary.org/search.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "docs": [
                    {"title": "No ISBN here", "author_name": ["Someone"]},
                    {"title": "Dune", "author_name": ["Frank Herbert"], "isbn": ["9780441172719"]},
                ]
            },
        )
    )
    client = make_client()

    results = await client.search("dune")

    assert len(results) == 1
    assert results[0].isbn == "9780441172719"
