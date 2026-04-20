from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    DB_URL: str = "sqlite:///./expenses.db"
    CHROMA_PATH: str = "./chroma_db"
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings() # type: ignore