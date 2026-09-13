from datetime import datetime
from typing import Annotated

from beanie import Document, Indexed


class CachedCover(Document):
    source_url: Annotated[str, Indexed(unique=True)]
    content_type: str
    data: bytes
    fetched_at: datetime

    class Settings:
        name = "cached_covers"
