import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = (os.getenv("Environment") or "dev")
    secretsManagerArn: str = os.getenv("SecretsManagerArn")

    model_config = SettingsConfigDict(env_file=".env") if os.path.isfile(".env") else SettingsConfigDict()

