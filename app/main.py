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

# 3. 初始化 Supabase
if not SUPABASE_URL or not SUPABASE_KEY:
    # 💡 這裡加上 print 方便在 Render Logs 看到具體少了什麼
    print(f"❌ 錯誤：環境變數缺失 URL={bool(SUPABASE_URL)}, KEY={bool(SUPABASE_KEY)}")
    # 部署環境建議不要直接 raise 導致整個 container 壞掉，可以先初始化為 None
    supabase = None 
else:
    print("✅ 成功：Supabase 環境變數已載入")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 4. CORS 設定 (保持不變)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://bloodtestapp-frontend.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 💡 新增部分：處理 Render 的 Health Check ---

# 解決 405 Method Not Allowed (HEAD /)
@app.get("/")
@app.head("/") # 👈 加上這個，Render 的 HEAD 檢查就不會噴 405 了
def read_root():
    return {
        "status": "ok", 
        "message": "Backend is running",
        "db_connected": SUPABASE_URL is not None
    }

# 解決 404 Not Found (/api/v1/health)
# 既然 Render 一直在找這個路徑，我們就直接給它一個
@app.get("/api/v1/health")
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "v1"}

# --- 💡 結束新增部分 ---

# 5. 引入並註冊路由
from app.routes import api_router
app.include_router(api_router, prefix="/api")

from app.scheduler import start_scheduler

@app.on_event("startup")
async def on_startup():
    # 建議先檢查變數再啟動，避免 Scheduler 因為沒 Key 崩潰
    if SUPABASE_URL and SUPABASE_KEY:
        start_scheduler()
        print("✅ Notification Scheduler Started")