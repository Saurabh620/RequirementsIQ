"""
RequirementIQ — Central Configuration
Loads all settings from environment variables via pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "RequirementIQ"
    app_env: str = "development"
    app_secret_key: str = "change-me"

    # MySQL
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "requirementiq"
    db_user: str = "root"
    db_password: str = ""
    db_pool_size: int = 5
    db_pool_recycle: int = 3600

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Option 1: Groq (free alternative) — get key at console.groq.com
    ai_provider: str = "groq"          # 'groq', 'mistral', 'openai'
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"  # free, very capable

    # Option 2: Mistral
    mistral_api_key: str = ""
    mistral_model: str = "mistral-large-latest"
    ai_temperature: float = 0.3
    ai_max_tokens_output: int = 3500
    ai_token_budget_per_request: int = 20000
    ai_max_retries: int = 2
    ai_timeout_seconds: int = 45

    # Auth
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Tier limits
    free_tier_monthly_docs: int = 3
    pro_tier_monthly_docs: int = 999999

    @property
    def db_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
