from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "transform-backend"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    aitunnel_api_key: SecretStr
    aitunnel_base_url: str = "https://api.aitunnel.ru/v1/"
    aitunnel_model: str = "gpt-5.6-luna"

    smtp_host: str = "smtp.yandex.ru"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: SecretStr = SecretStr("")

    database_url: SecretStr

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
