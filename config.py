from pydantic import Json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    market_data_cache_config: Json[dict[str, str]]
    market_data_client_config: Json[dict[str, str]]
