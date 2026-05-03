from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vivolog"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/vivolog"

    model_config = {"env_prefix": "VIVOLOG_", "env_file": ".env"}


settings = Settings()
