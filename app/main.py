from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os

# 假設你已經有 api_router，保留它
# from app.routes import api_router 

app = FastAPI(title="Dad's BP Tracker API")

# 1. Supabase 設定 (請確保這些環境變數在 Render 或 .env 中已設定)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://localhost:5173", 
        "https://bloodtestapp-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend for Dad's BP Tracker is running"}

# 3. 核心邏輯：提交血壓並獲取推薦
@app.post("/api/v1/health-record")
async def create_health_record(record: dict):
    """
    接收參數: user_id, systolic, diastolic, pulse, weight, height
    1. 計算 BMI & 血壓等級
    2. 存入 health_logs
    3. 從 diet_templates 撈取建議
    """
    try:
        user_id = record.get("user_id")
        sys = record.get("systolic")
        dia = record.get("diastolic")
        weight = record.get("weight")
        height = record.get("height")
        
        # A. 計算血壓等級 (對應你的 bp_category 欄位)
        bp_level = "Normal"
        if sys >= 140 or dia >= 90:
            bp_level = "High"
        elif sys >= 120 or dia >= 80:
            bp_level = "Elevated"

        # B. 計算 BMI
        bmi = round(weight / ((height / 100) ** 2), 2)

        # C. 存入 Supabase health_logs
        log_data = {
            "user_id": user_id,
            "systolic": sys,
            "diastolic": dia,
            "pulse": record.get("pulse"),
            "bp_level": bp_level, # 存入這個欄位方便行事曆變色
            "period": record.get("period", "morning")
        }
        supabase.table("health_logs").insert(log_data).execute()

        # D. 從 diet_templates 撈取推薦 (匹配 bp_category 並找 BMI 最接近的)
        # 邏輯：篩選同血壓等級，並依 BMI 差值排序取第一筆
        recommend_resp = supabase.table("diet_templates") \
            .select("*") \
            .eq("bp_category", bp_level) \
            .order("bmi", desc=False) \
            .limit(20) \
            .execute()
        
        # 在 Python 端找 BMI 最接近的一筆
        templates = recommend_resp.data
        best_match = min(templates, key=lambda x: abs(float(x['bmi']) - bmi)) if templates else None

        return {
            "status": "success",
            "bp_level": bp_level,
            "bmi": bmi,
            "recommendation": {
                "meal_plan": best_match.get("recommended_meal_plan") if best_match else "均衡飲食",
                "calories": best_match.get("recommended_calories") if best_match else 2000,
                "protein": best_match.get("recommended_protein") if best_match else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# 如果你有 router 資料夾，記得最後載入
# app.include_router(api_router, prefix="/api")