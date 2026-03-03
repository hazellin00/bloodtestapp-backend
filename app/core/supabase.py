import os
from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    # Ensure the environment variables are explicitly set before calling create_client
    url: str = settings.supabase_url
    key: str = settings.supabase_key
    if not url or not key:
        raise ValueError("Supabase URL and Key must be provided in the environment variables.")
    return create_client(url, key)
