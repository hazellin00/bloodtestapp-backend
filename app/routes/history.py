from fastapi import APIRouter, HTTPException
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
import os
from uuid import UUID
from ..database import supabase  # 確保路徑正確

# 💡 修正：使用 Google 官方推薦的新版導入方式
from google import genai 

# 💡 修正 1: 移除重複的 prefix，讓路徑保持為 /api/history
router = APIRouter(tags=["Health History"])

# 💡 配置 Gemini (使用 2026 最新 Client 語法)
# 如果環境變數讀取有問題，這裡會直接報錯，方便偵錯
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ 警告：找不到 GEMINI_API_KEY 環境變數")

client = genai.Client(api_key=api_key)

# 定義資料格式
class HealthLogCreate(BaseModel):
    user_id: UUID  # 嚴格限制必須是 UUID 格式
    systolic: int
    diastolic: int
    pulse: int
    period: str  # 早上/晚上

# --- 1. 儲存血壓 (爸爸端新增資料用) ---
@router.post("/")
async def create_log(log: HealthLogCreate):
    """ 儲存爸爸量測的血壓 """
    data = {
        "user_id": str(log.user_id),
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

# --- 2. 獲取日總結 (爸爸端自己看紀錄用) ---
@router.get("/{user_id}/{target_date}")
async def get_daily_summary(user_id: UUID, target_date: date):
    """ 獲取特定日期的紀錄與 AI 暖心回顧 (本人視角) """
    start_time = datetime.combine(target_date, datetime.min.time()).isoformat()
    end_time = datetime.combine(target_date, datetime.max.time()).isoformat()

    response = supabase.table("health_logs") \
        .select("*") \
        .eq("user_id", str(user_id)) \
        .gte("created_at", start_time) \
        .lte("created_at", end_time) \
        .execute()

    logs = response.data
    if not logs:
        return {"date": target_date, "logs": [], "summary": "今天還沒量血壓喔！"}

    # 整理數據給 AI
    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}, 心跳:{l['pulse']}" for l in logs])
    
    prompt = f"這是我在 {target_date} 的血壓紀錄：\n{log_text}\n請給我兩句繁體中文的健康回顧建議，結尾須包含醫療免責聲明。"
    
    try:
        # 💡 使用新版 client.models.generate_content 語法
        ai_res = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        summary = ai_res.text
    except Exception as e:
        print(f"🚨 爸爸端 AI 出錯: {e}")
        summary = "數據已存檔，請參考數值。"

    return {"date": target_date, "logs": logs, "summary": summary}

# --- 3. 獲取爸爸日總結 (女兒端專用) ---
@router.get("/family-history/{daughter_id}/{target_date}")
async def get_dad_history(daughter_id: UUID, target_date: date):
    """ 女兒專用：透過綁定關係，抓取爸爸的血壓紀錄與 AI 回顧 """
    
    # 步驟 1：去 family_links 查這個女兒綁定了哪位爸爸
    link_res = supabase.table("family_links").select("parent_id").eq("child_id", str(daughter_id)).execute()
    
    if not link_res.data:
        raise HTTPException(status_code=404, detail="尚未綁定爸爸的帳號喔！")
        
    dad_id = link_res.data[0]["parent_id"]

    # 步驟 2：拿著爸爸的 ID，去 health_logs 撈資料
    start_time = datetime.combine(target_date, datetime.min.time()).isoformat()
    end_time = datetime.combine(target_date, datetime.max.time()).isoformat()

    logs_res = supabase.table("health_logs") \
        .select("*") \
        .eq("user_id", dad_id) \
        .gte("created_at", start_time) \
        .lte("created_at", end_time) \
        .execute()
        
    logs = logs_res.data
    if not logs:
        return {"dad_id": dad_id, "date": target_date, "logs": [], "summary": "爸爸今天還沒量血壓喔！記得傳個訊息提醒他。"}

    # 步驟 3：整理數據給 AI
    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}, 心跳:{l['pulse']}" for l in logs])
    
    prompt = f"這是我父親在 {target_date} 的血壓紀錄：\n{log_text}\n我是他女兒，請用女兒關心爸爸的口吻，寫兩句繁體中文暖心回顧給我。結尾須包含醫療免責聲明。"
    
    try:
        # 💡 確保這裡也使用新版 Client 語法
        ai_res = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        summary = ai_res.text
    except Exception as e:
        print(f"🚨 女兒端 AI 出錯: {e}")
        summary = "數據已存檔，請參考數值。"

    return {"dad_id": dad_id, "date": target_date, "logs": logs, "summary": summary}