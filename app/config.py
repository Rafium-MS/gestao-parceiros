from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "gestao-parceiros"
    env: str = "dev"
    debug: bool = True
    database_url: AnyUrl
    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()
