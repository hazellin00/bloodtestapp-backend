import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

# 1. 取得路徑並載入環境變數
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Dad's BP Tracker API")

# 2. 讀取變數
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# 3. 只有在「真的沒讀到」時才報錯
if not SUPABASE_URL or not SUPABASE_KEY:
    print(f"❌ 錯誤：無法從 {env_path} 讀取環境變數")
    raise ValueError("找不到 Supabase 環境變數，請檢查 .env 檔案內容")
else:
    print("✅ 成功：Supabase 環境變數已載入")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 4. CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://bloodtestapp-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 引入並註冊路由 (務必放在載入變數之後)
from app.routes import api_router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "message": "Backend is running",
        "db_connected": SUPABASE_URL is not None
    }

