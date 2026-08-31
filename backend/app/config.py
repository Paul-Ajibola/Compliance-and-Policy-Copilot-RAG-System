from pydantic_settings import BaseSettings, SettingsConfigDict

# class for settings
class Settings(BaseSettings):
    environment: str = "local"
    database_url: str

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "compliance_copilot"

    # write rules telling Settings() how to operate
    model_config = SettingsConfigDict(
        env_file=".env.local",    # look at the files named .env.local
        env_file_encoding="utf-8",      # read it with the UTF-8 test formatting
        extra="ignore",           # ignore any extra variable in .env not listed. don't crash the app
    )


settings = Settings()

# logging
logger = logging.getLogger(__name__)


