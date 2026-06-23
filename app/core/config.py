from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="IMS_")

    database_url: str = "sqlite:///./insurance.db"
    app_name: str = "Insurance Management System"


settings = Settings()
