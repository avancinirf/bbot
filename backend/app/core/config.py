from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/binance_bot.db"

    # Binance API keys (vamos usar depois; em modo simulado podem ficar vazias)
    BINANCE_API_KEY: str | None = None
    BINANCE_API_SECRET: str | None = None

    # Flag global de modo simulado
    SIMULATION_MODE: bool = True

    # Config para ler .env
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
