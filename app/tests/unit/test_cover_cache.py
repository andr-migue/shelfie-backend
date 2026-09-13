import httpx
import pytest

from app.core.exceptions import CoverHostNotAllowedError, CoverNotFoundError
from app.models.cached_cover import CachedCover
from app.services import cover_cache

COVER_URL = "https://covers.openlibrary.org/b/id/12054527-M.jpg"


def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


async def test_get_cover_rejects_disallowed_host():
    with pytest.raises(CoverHostNotAllowedError):
        await cover_cache.get_cover("https://evil.example.com/whatever.jpg", make_client())


async def test_get_cover_downloads_and_caches(respx_mock):
    route = respx_mock.get(COVER_URL).mock(
        return_value=httpx.Response(200, content=b"fake-image-bytes", headers={"content-type": "image/jpeg"})
    )
    client = make_client()

    first = await cover_cache.get_cover(COVER_URL, client)
    second = await cover_cache.get_cover(COVER_URL, client)

    assert first == (b"fake-image-bytes", "image/jpeg")
    assert second == (b"fake-image-bytes", "image/jpeg")
    assert route.call_count == 1
    assert await CachedCover.find_one(CachedCover.source_url == COVER_URL) is not None


async def test_get_cover_raises_when_not_found(respx_mock):
    respx_mock.get(COVER_URL).mock(return_value=httpx.Response(404))
    client = make_client()

    with pytest.raises(CoverNotFoundError):
        await cover_cache.get_cover(COVER_URL, client)


async def test_get_cover_follows_redirects(respx_mock):
    redirect_target = "https://archive.org/download/m_covers_0008/m_covers_0008_45.zip/0008457619-M.jpg"
    respx_mock.get(COVER_URL).mock(
        return_value=httpx.Response(302, headers={"location": redirect_target})
    )
    respx_mock.get(redirect_target).mock(
        return_value=httpx.Response(200, content=b"archived-image-bytes", headers={"content-type": "image/jpeg"})
    )
    client = make_client()

    data, content_type = await cover_cache.get_cover(COVER_URL, client)

    assert data == b"archived-image-bytes"
    assert content_type == "image/jpeg"
    assert await CachedCover.find_one(CachedCover.source_url == COVER_URL) is not None
