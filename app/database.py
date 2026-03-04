import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. 取得 .env 路徑並載入
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. 讀取環境變數
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")

# 3. 檢查變數（保留錯誤拋出，但刪除中間的 print）
if not url or not key:
    # 💡 這裡只保留 raise，讓程式在沒變數時斷開，但不印出敏感路徑
    raise ValueError("❌ 錯誤：找不到環境變數 SUPABASE_URL 或 SUPABASE_ANON_KEY")

# 4. 初始化連線
supabase: Client = create_client(url, key)
