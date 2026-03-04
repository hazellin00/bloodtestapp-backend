from fastapi import APIRouter, HTTPException
from datetime import date, datetime
from typing import List, Dict, Any
from uuid import UUID

# 💡 1. 引入 Supabase 與 AI 服務
from ..database import supabase  
from app.services.ai import generate_health_advice

# 💡 2. 引入剛寫好的 Pydantic 模型 (Schemas)
from schema_setup import HealthLogCreate, HealthLogResponse

router = APIRouter(tags=["Health History"])

# --- 1. 儲存血壓 (加入 response_model) ---
@router.post("/", response_model=HealthLogResponse)
async def create_log(log: HealthLogCreate):
    """ 儲存血壓紀錄，並回傳格式化後的資料 """
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
    
    # 這裡回傳的資料會自動被 HealthLogResponse 驗證並過濾
    return response.data[0]


# --- 2. 獲取日總結 (本人視角) ---
@router.get("/{user_id}/{target_date}")
async def get_daily_summary(user_id: UUID, target_date: date):
    """ 獲取特定日期的紀錄與動態 AI 暖心回顧 """
    
    # A. 抓取該用戶真實的個人檔案 (用於 AI)
    profile_res = supabase.table("profiles") \
        .select("age, bmi") \
        .eq("id", str(user_id)) \
        .execute()
    
    user_data = profile_res.data[0] if profile_res.data else {"age": "未知", "bmi": "未知"}

    # B. 撈取當日血壓紀錄
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

    # C. 整理數據並呼叫統一的 AI 服務
    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}, 心跳:{l['pulse']}" for l in logs])
    
    try:
        summary = await generate_health_advice(
            user_profile={
                "age": user_data.get("age"), 
                "bmi": user_data.get("bmi")
            },
            daily_logs=log_text,
            template_data={} # 日總結暫不掛載 Kaggle 模板
        )
    except Exception as e:
        print(f"🚨 AI Error: {e}")
        summary = "數據已記錄。請保持愉快心情。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"

    return {
        "date": target_date, 
        "logs": logs, 
        "summary": summary,
        "profile_snapshot": user_data # 回傳當下的 BMI 狀態給前端
    }


# --- 3. 獲取爸爸日總結 (女兒端視角) ---
@router.get("/family-history/{daughter_id}/{target_date}")
async def get_dad_history(daughter_id: UUID, target_date: date):
    """ 女兒專用：透過綁定關係獲取資料與女兒口吻的 AI 回顧 """
    
    # 步驟 1：找尋綁定的爸爸 ID
    link_res = supabase.table("family_links").select("parent_id").eq("child_id", str(daughter_id)).execute()
    if not link_res.data:
        raise HTTPException(status_code=404, detail="尚未綁定家人帳號")
        
    dad_id = link_res.data[0]["parent_id"]

    # 步驟 2：獲取爸爸的個人檔案
    dad_profile = supabase.table("profiles").select("age, bmi, name").eq("id", dad_id).execute()
    dad_info = dad_profile.data[0] if dad_profile.data else {"age": "未知", "bmi": "未知", "name": "爸爸"}

    # 步驟 3：獲取血壓紀錄
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
        return {"dad_name": dad_info.get("name"), "summary": "爸爸今天還沒量血壓喔。"}

    # 步驟 4：呼叫 AI (設定為女兒口吻)
    log_text = "\n".join([f"{l['period']}: {l['systolic']}/{l['diastolic']}, 心跳:{l['pulse']}" for l in logs])
    
    try:
        summary = await generate_health_advice(
            user_profile={
                "age": dad_info.get("age"),
                "bmi": dad_info.get("bmi"),
                "relation": "daughter" # 告訴 AI 這是女兒視角
            },
            daily_logs=log_text,
            template_data={}
        )
    except Exception:
        summary = "數據已同步。請提醒爸爸注意休息。"

    return {
        "dad_id": dad_id,
        "dad_name": dad_info.get("name"),
        "date": target_date,
        "logs": logs,
        "summary": summary
    }