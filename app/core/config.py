from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongodb_uri: str
    database_name: str
    open_library_base_url: str = "https://openlibrary.org"
    http_timeout: float = 5.0
    cors_origins: list[str] = ["http://localhost:5173"]

settings = Settings()