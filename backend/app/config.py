from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "compliance_copilot"

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# logging
logger = logging.getLogger(__name__)