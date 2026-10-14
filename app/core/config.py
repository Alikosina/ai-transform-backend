from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "transform-backend"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    database_url: SecretStr

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
