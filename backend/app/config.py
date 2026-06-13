from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./personal_ai.db"
    GEMINI_API_KEY: str = ""
    DEFAULT_USER_ID: int = 1

    class Config:
        env_file = ".env"


settings = Settings()
