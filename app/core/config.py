from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Atlas Wealth"
    secret_key: str = "dev-secret"
    database_url: str = "sqlite:///./atlas_wealth.db"
    tax_regime_default: str = "lucro_presumido"
    default_real_return: float = 0.06
    default_inflation: float = 0.04
    default_cdi: float = 0.115

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
