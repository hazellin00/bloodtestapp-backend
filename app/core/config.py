from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    gemini_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
