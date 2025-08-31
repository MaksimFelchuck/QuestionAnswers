from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "QuestionAnswers API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for questions and answers"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
