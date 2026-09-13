import pytest
from fastapi import HTTPException

from app.core.dependencies import get_book_client
from app.services.cached_book_client import CachedBookClient


class _FakeAppState:
    open_library_http_client = object()


class _FakeApp:
    state = _FakeAppState()


class _FakeRequest:
    app = _FakeApp()


def test_defaults_to_configured_provider_when_no_query_param():
    client = get_book_client(_FakeRequest(), provider=None)

    assert isinstance(client, CachedBookClient)


def test_accepts_explicit_open_library_provider():
    client = get_book_client(_FakeRequest(), provider="open_library")

    assert isinstance(client, CachedBookClient)


def test_rejects_unknown_provider():
    with pytest.raises(HTTPException) as exc_info:
        get_book_client(_FakeRequest(), provider="does_not_exist")

    assert exc_info.value.status_code == 400
