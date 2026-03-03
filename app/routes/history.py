from fastapi import APIRouter, HTTPException
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
import os
from ..database import supabase  # 確保路徑正確
import google.generativeai as genai

# 💡 修正 1: 移除重複的 prefix，讓路徑保持為 /api/history
router = APIRouter(tags=["Health History"])

# 配置 Gemini (使用穩定版語法)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 定義資料格式
class HealthLogCreate(BaseModel):
    user_id: str
    systolic: int
    diastolic: int
    pulse: int
    period: str  # 早上/中午/晚上

# --- 1. 儲存血壓 (這是你前端 POST 失敗的地方) ---
@router.post("/")
async def create_log(log: HealthLogCreate):
    """ 儲存爸爸量測的血壓 """
    data = {
        "user_id": log.user_id,
        "systolic": log.systolic,
        "diastolic": log.diastolic,
        "pulse": log.pulse,
        "period": log.period,
        "created_at": datetime.now().isoformat()
    }
    
    response = supabase.table("health_logs").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="儲存失敗")
    
    return {"status": "success", "data": response.data[0]}

# --- 2. 獲取日總結 (女兒端查詢用) ---
@router.get("/{user_id}/{target_date}")
async def get_daily_summary(user_id: str, target_date: date):
    """ 獲取特定日期的紀錄與 AI 暖心回顧 """
    start_time = datetime.combine(target_date, datetime.min.time()).isoformat()
    end_time = datetime.combine(target_date, datetime.max.time()).isoformat()

    response = supabase.table("health_logs") \
        .select("*") \
        .eq("user_id", user_id) \
        .gte("created_at", start_time) \
        .lte("created_at", end_time) \
        .execute()

    logs = response.data
    if not logs:
        return {"date": target_date, "logs": [], "summary": "今天還沒量血壓喔！"}

    # 整理數據給 AI
    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}" for l in logs])
    
    prompt = f"我父親在 {target_date} 的血壓紀錄：\n{log_text}\n請寫兩句繁體中文暖心回顧，結尾須包含醫療免責聲明。"
    
    try:
        ai_res = model.generate_content(prompt)
        summary = ai_res.text
    except:
        summary = "數據已存檔，請參考數值。"

    return {"date": target_date, "logs": logs, "summary": summary}