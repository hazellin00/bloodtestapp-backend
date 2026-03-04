from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# 找到專案根目錄
base_dir = Path(__file__).resolve().parent.parent.parent
env_file = base_dir / ".env"

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str 
    gemini_api_key: str

    model_config = SettingsConfigDict(
        env_file=str(env_file),
        env_file_encoding='utf-8',
        extra='ignore' 
    )

settings = Settings()