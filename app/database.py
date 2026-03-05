import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions

# 1. 取得 .env 路徑並載入
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. 讀取環境變數
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")

# 3. 檢查變數
if not url or not key:
    raise ValueError("❌ 錯誤：找不到環境變數 SUPABASE_URL 或 SUPABASE_ANON_KEY")

# 4. 初始化連線 — 關閉 HTTP/2 以防止 StreamReset 錯誤
# httpx 的 HTTP/2 在長連線下有已知 Bug，停用後可避免 500 Internal Server Error
custom_http_client = httpx.Client(http2=False)
supabase: Client = create_client(
    url,
    key,
    options=ClientOptions(httpx_client=custom_http_client)
)
