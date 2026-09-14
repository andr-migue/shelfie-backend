from app.core.protocols import BookMetadata
from app.services.cached_book_client import CachedBookClient

BOOK = BookMetadata(
    title="Nineteen Eighty-Four",
    authors=["George Orwell"],
    isbn="0451524934",
    cover_url="https://covers.openlibrary.org/b/id/12054527-M.jpg",
    publisher="Signet Classics",
    published_year=1993,
    page_count=328,
)


class FakeBookClient:
    def __init__(self, book: BookMetadata | None = None, search_results: list[BookMetadata] | None = None) -> None:
        self._book = book
        self._search_results = search_results or []
        self.get_by_isbn_calls = 0
        self.search_calls = 0

    async def get_by_isbn(self, isbn: str) -> BookMetadata | None:
        self.get_by_isbn_calls += 1
        return self._book

    async def search(self, query: str) -> list[BookMetadata]:
        self.search_calls += 1
        return self._search_results


async def test_get_by_isbn_caches_result_after_first_call():
    inner = FakeBookClient(book=BOOK)
    client = CachedBookClient(inner, provider="open_library")

    first = await client.get_by_isbn(BOOK.isbn)
    second = await client.get_by_isbn(BOOK.isbn)

    assert first == BOOK
    assert second == BOOK
    assert inner.get_by_isbn_calls == 1


async def test_get_by_isbn_caches_not_found_result():
    inner = FakeBookClient(book=None)
    client = CachedBookClient(inner, provider="open_library")

    first = await client.get_by_isbn("0000000000")
    second = await client.get_by_isbn("0000000000")

    assert first is None
    assert second is None
    assert inner.get_by_isbn_calls == 1


async def test_search_caches_result_after_first_call():
    inner = FakeBookClient(search_results=[BOOK])
    client = CachedBookClient(inner, provider="open_library")

    first = await client.search("1984")
    second = await client.search("1984")

    assert first == [BOOK]
    assert second == [BOOK]
    assert inner.search_calls == 1


async def test_search_cache_key_ignores_case_and_surrounding_whitespace():
    inner = FakeBookClient(search_results=[BOOK])
    client = CachedBookClient(inner, provider="open_library")

    await client.search("1984")
    await client.search("  1984  ")
    await client.search("1984".upper())

    assert inner.search_calls == 1


async def test_search_for_different_queries_does_not_share_cache():
    inner = FakeBookClient(search_results=[BOOK])
    client = CachedBookClient(inner, provider="open_library")

    await client.search("1984")
    await client.search("dune")

    assert inner.search_calls == 2


async def test_same_query_with_different_provider_does_not_share_cache():
    inner_open_library = FakeBookClient(search_results=[BOOK])
    inner_google_books = FakeBookClient(search_results=[BOOK])
    open_library_client = CachedBookClient(inner_open_library, provider="open_library")
    google_books_client = CachedBookClient(inner_google_books, provider="google_books")

    await open_library_client.search("dune")
    await google_books_client.search("dune")

    assert inner_open_library.search_calls == 1
    assert inner_google_books.search_calls == 1


async def test_same_isbn_with_different_provider_does_not_share_cache():
    inner_open_library = FakeBookClient(book=BOOK)
    inner_google_books = FakeBookClient(book=BOOK)
    open_library_client = CachedBookClient(inner_open_library, provider="open_library")
    google_books_client = CachedBookClient(inner_google_books, provider="google_books")

    await open_library_client.get_by_isbn(BOOK.isbn)
    await google_books_client.get_by_isbn(BOOK.isbn)

    assert inner_open_library.get_by_isbn_calls == 1
    assert inner_google_books.get_by_isbn_calls == 1
