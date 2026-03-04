import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 才會去讀取 .env 檔案
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")

# 檢查變數是否真的有讀到
if not url or not key:
    print(" 錯誤：找不到 Supabase 環境變數，請檢查 .env 檔案")
    # 這裡可以拋出錯誤，防止程式在錯誤狀態下繼續執行
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY are required")

supabase: Client = create_client(url, key)