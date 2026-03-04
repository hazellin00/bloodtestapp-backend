from fastapi import APIRouter, HTTPException
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel
import os
from uuid import UUID
from ..database import supabase  # 確保路徑正確
from app.services.ai import generate_health_advice


# 移除重複的 prefix，讓路徑保持為 /api/history
router = APIRouter(tags=["Health History"])

# 定義資料格式
class HealthLogCreate(BaseModel):
    user_id: UUID  # 嚴格限制必須是 UUID 格式
    systolic: int
    diastolic: int
    pulse: int
    period: str  

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

# --- 2. 獲取日總結 (動態抓取個人檔案) ---
@router.get("/{user_id}/{target_date}")
async def get_daily_summary(user_id: UUID, target_date: date):
    """ 獲取特定日期的紀錄與 AI 暖心回顧 """
    
    # 💡 A. 先去 profiles 表格抓取該用戶的真實年齡與 BMI
    profile_res = supabase.table("profiles") \
        .select("age, bmi") \
        .eq("id", str(user_id)) \
        .execute()
    
    # 如果抓不到資料，給予預設值
    user_data = profile_res.data[0] if profile_res.data else {"age": "未知", "bmi": "未知"}

    # B. 撈取血壓紀錄 (原本的邏輯)
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

    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}, 心跳:{l['pulse']}" for l in logs])
    
    # 💡 C. 呼叫 AI，傳入真實的年齡與 BMI
    try:
        summary = await generate_health_advice(
            user_profile={
                "age": user_data.get("age", "未知"), 
                "bmi": user_data.get("bmi", "未知")
            },
            daily_logs=log_text,
            template_data={} # 日總結暫不使用 Kaggle 模板
        )
    except Exception as e:
        summary = "數據已存檔。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"

    return {"date": target_date, "logs": logs, "summary": summary}


# --- 3. 獲取爸爸日總結 (女兒端專用：動態抓取資料) ---
@router.get("/family-history/{daughter_id}/{target_date}")
async def get_dad_history(daughter_id: UUID, target_date: date):
    """ 女兒專用：透過綁定關係，抓取爸爸的個人資料、血壓紀錄與 AI 回顧 """
    
    # 步驟 1：去 family_links 查這個女兒綁定了哪位爸爸
    link_res = supabase.table("family_links").select("parent_id").eq("child_id", str(daughter_id)).execute()
    
    if not link_res.data:
        raise HTTPException(status_code=404, detail="尚未綁定爸爸的帳號喔！")
        
    dad_id = link_res.data[0]["parent_id"]

    # 💡 步驟 2：新增！拿著爸爸的 ID，去 profiles 撈他的年齡和 BMI
    dad_profile_res = supabase.table("profiles") \
        .select("age, bmi, name") \
        .eq("id", dad_id) \
        .execute()
    
    # 如果 profiles 沒資料，給個保險值
    dad_info = dad_profile_res.data[0] if dad_profile_res.data else {"age": "未知", "bmi": "未知", "name": "爸爸"}

    # 步驟 3：拿著爸爸的 ID，去 health_logs 撈血壓資料
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
        return {
            "dad_id": dad_id, 
            "dad_name": dad_info.get("name"),
            "date": target_date, 
            "logs": [], 
            "summary": f"{dad_info.get('name')}今天還沒量血壓喔！記得提醒他。"
        }

    # 步驟 4：整理數據給 AI
    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}, 心跳:{l['pulse']}" for l in logs])
    
    # 💡 步驟 5：呼叫統一的 AI 函式，傳入爸爸的真實數據
    # 同時可以在 user_profile 多傳一個 role 讓 AI 知道要用女兒口吻
    try:
        summary = await generate_health_advice(
            user_profile={
                "age": dad_info.get("age"),
                "bmi": dad_info.get("bmi"),
                "relation": "daughter", # 告訴 AI 這是女兒在看
                "subject": "父親"
            },
            daily_logs=log_text,
            template_data={} # 女兒端的日回顧暫不需 Kaggle 模板
        )
    except Exception as e:
        print(f"🚨 女兒端 AI 出錯: {e}")
        summary = "數據已存檔，請參考數值。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"

    return {
        "dad_id": dad_id, 
        "dad_name": dad_info.get("name"),
        "date": target_date, 
        "logs": logs, 
        "summary": summary
    }