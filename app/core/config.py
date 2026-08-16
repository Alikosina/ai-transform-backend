from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "transform-backend"
    debug: bool = False

    ollama_base_url: str = "http://31.128.43.101:11434"
    ollama_model: str = "llama3.2"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
