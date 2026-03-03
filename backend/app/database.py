import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 強制讀取專案根目錄或當前目錄的 .env
load_dotenv()

# 確保名稱與您的 .env 檔案完全一致
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("錯誤：找不到 SUPABASE_URL 或 SUPABASE_KEY，請檢查 .env 檔案")

supabase: Client = create_client(url, key)