from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    DB_URL: str = "sqlite:///./expenses.db"
    MODEL_NAME: str = "all-MiniLM-L6-v2"

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "finance_tips"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() # type: ignore