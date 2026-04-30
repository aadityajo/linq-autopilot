from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    linq_api_key: str = ""
    linq_webhook_secret: str = ""
    database_url: str = "sqlite:///./autopilot.db"
    bluebubbles_url: str = ""
    bluebubbles_password: str = ""
    lmstudio_base_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
