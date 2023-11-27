from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TABLE_NAME: str = "users"

    ROWS: int = 10
    COLUMNS: int = 10
    COLUMN_WIDTH: int = 100
    ROW_HEIGHT: int = 30

    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600

    API_KEY: str
    FILE_ID: str

    class Config:
        env_file = "project.env", ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
