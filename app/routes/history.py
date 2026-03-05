from fastapi import APIRouter, HTTPException
from datetime import date, datetime, timedelta, timezone

TW_TZ = timezone(timedelta(hours=8))
from typing import List, Dict, Any
from uuid import UUID

# 💡 1. 引入 Supabase 與 AI 服務
from ..database import supabase  
from app.services.ai import generate_health_advice

# 💡 2. 引入剛寫好的 Pydantic 模型 (Schemas)
from schema_setup import HealthLogCreate, HealthLogResponse
from pydantic import BaseModel

router = APIRouter(tags=["Health History"])

class FamilyBindRequest(BaseModel):
    parent_id: str
    child_id: str

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
        "created_at": datetime.now(TW_TZ).isoformat()
    }
    
    response = supabase.table("health_logs").insert(data).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="儲存失敗")
    
    # 這裡回傳的資料會自動被 HealthLogResponse 驗證並過濾
    return response.data[0]


# --- 2.5 獲取個人歷史區間 (本人視角) ---
@router.get("/range/{user_id}")
async def get_history_range(user_id: str, start_date: date, end_date: date):
    """ 本人專用：獲取指定區間內的血壓紀錄與統計 """
    
    start_time = datetime.combine(start_date, datetime.min.time(), tzinfo=TW_TZ).isoformat()
    end_time = datetime.combine(end_date, datetime.max.time(), tzinfo=TW_TZ).isoformat()

    logs_res = supabase.table("health_logs") \
        .select("*") \
        .eq("user_id", str(user_id)) \
        .gte("created_at", start_time) \
        .lte("created_at", end_time) \
        .order("created_at", desc=False) \
        .execute()
        
    logs = logs_res.data
    
    # 獲取個人檔案
    profile_res = supabase.table("profiles").select("age, bmi, name").eq("id", str(user_id)).execute()
    profile_info = profile_res.data[0] if profile_res.data else {"age": "未知", "bmi": "未知", "name": "長輩"}

    # 如果沒有紀錄就提早回傳
    if not logs:
        return {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
            "logs": [],
            "summary": "這段期間還沒有測量紀錄喔。"
        }
        
    avg_sys = sum(l['systolic'] for l in logs) // len(logs)
    avg_dia = sum(l['diastolic'] for l in logs) // len(logs)
    high_count = sum(1 for l in logs if l['systolic'] >= 140 or l['diastolic'] >= 90)
    
    summary_text = f"區間: {start_date} 到 {end_date} (共 {len(logs)} 筆紀錄)。平均血壓 {avg_sys}/{avg_dia}。其中有 {high_count} 筆偏高。"
    
    try:
        summary = await generate_health_advice(
            user_profile={
                "age": profile_info.get("age"),
                "bmi": profile_info.get("bmi")
            },
            daily_logs=summary_text,
            template_data={}
        )
    except Exception as e:
        print(f"🚨 AI Error in range: {e}")
        summary = f"這段期間您共測量了 {len(logs)} 次，平均血壓為 {avg_sys}/{avg_dia}。"

    return {
        "user_id": user_id,
        "user_name": profile_info.get("name"),
        "start_date": start_date,
        "end_date": end_date,
        "logs": logs,
        "summary": summary
    }


# --- 2. 獲取日總結 (本人視角) ---
@router.get("/{user_id}/{target_date}")
async def get_daily_summary(user_id: str, target_date: date):
    """ 獲取特定日期的紀錄與動態 AI 暖心回顧 """
    
    # A. 抓取該用戶真實的個人檔案 (用於 AI)
    profile_res = supabase.table("profiles") \
        .select("age, bmi") \
        .eq("id", str(user_id)) \
        .execute()
    
    user_data = profile_res.data[0] if profile_res.data else {"age": "未知", "bmi": "未知"}

    # B. 撈取當日血壓紀錄
    start_time = datetime.combine(target_date, datetime.min.time(), tzinfo=TW_TZ).isoformat()
    end_time = datetime.combine(target_date, datetime.max.time(), tzinfo=TW_TZ).isoformat()

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
        "profile_snapshot": user_data 
    }


# --- 3. 獲取爸爸歷史區間 (女兒端視角 - 支援 7天/30天/1年/自訂) ---
# ⚠️ 注意這段必須放在單日的上面，否則 FastAPI 會把 "range" 當成 {daughter_id}
@router.get("/family-history/range/{daughter_id}")
async def get_dad_history_range(daughter_id: str, start_date: date, end_date: date):
    """ 女兒專用：獲取指定區間內的血壓紀錄 """
    
    # 步驟 1：找尋綁定的爸爸 ID
    link_res = supabase.table("family_links").select("parent_id").eq("child_id", str(daughter_id)).execute()
    if not link_res.data:
        raise HTTPException(status_code=404, detail="尚未綁定家人帳號")
        
    dad_id = link_res.data[0]["parent_id"]

    # 步驟 2：獲取血壓紀錄
    start_time = datetime.combine(start_date, datetime.min.time(), tzinfo=TW_TZ).isoformat()
    end_time = datetime.combine(end_date, datetime.max.time(), tzinfo=TW_TZ).isoformat()

    logs_res = supabase.table("health_logs") \
        .select("*") \
        .eq("user_id", dad_id) \
        .gte("created_at", start_time) \
        .lte("created_at", end_time) \
        .order("created_at", desc=False) \
        .execute()
        
    logs = logs_res.data
    
    # 如果沒有紀錄就提早回傳
    if not logs:
        return {
            "dad_id": dad_id,
            "start_date": start_date,
            "end_date": end_date,
            "logs": [],
            "summary": "這段期間爸爸尚未測量血壓喔。"
        }
        
    # 計算平均值供 AI 快速參考，避免長天期資料塞爆 Token
    avg_sys = sum(l['systolic'] for l in logs) // len(logs)
    avg_dia = sum(l['diastolic'] for l in logs) // len(logs)
    high_count = sum(1 for l in logs if l['systolic'] >= 140 or l['diastolic'] >= 90)
    
    # 步驟 3：獲取爸爸的個人檔案
    dad_profile = supabase.table("profiles").select("age, bmi, name").eq("id", dad_id).execute()
    dad_info = dad_profile.data[0] if dad_profile.data else {"age": "未知", "bmi": "未知", "name": "爸爸"}

    # 步驟 4：呼叫 AI (給予區間總結)
    # 不傳所有原始資料，改傳統計摘要給 AI
    summary_text = f"區間: {start_date} 到 {end_date} (共 {len(logs)} 筆紀錄)。平均血壓 {avg_sys}/{avg_dia}。其中有 {high_count} 筆偏高。"
    
    try:
        summary = await generate_health_advice(
            user_profile={
                "age": dad_info.get("age"),
                "bmi": dad_info.get("bmi"),
                "relation": "daughter"
            },
            daily_logs=summary_text,
            template_data={}
        )
    except Exception as e:
        print(f"🚨 AI Error in range: {e}")
        summary = f"這段期間爸爸共測量了 {len(logs)} 次，平均血壓為 {avg_sys}/{avg_dia}。"

    return {
        "dad_id": dad_id,
        "dad_name": dad_info.get("name"),
        "start_date": start_date,
        "end_date": end_date,
        "logs": logs,
        "summary": summary
    }


# --- 5. 綁定家庭帳號 ---
@router.post("/family-history/bind")
async def bind_family_account(request: FamilyBindRequest):
    """ 將女兒的帳號綁定到指定的爸爸(家長)帳號 """
    
    # 檢查爸爸的帳號是否存在 (必須要有關聯的 profile 才算有效)
    parent_res = supabase.table("profiles").select("id").eq("id", str(request.parent_id)).execute()
    if not parent_res.data:
        raise HTTPException(status_code=404, detail="找不到這個金鑰對應的家人資料，請確認金鑰是否正確。")

    # 寫入家庭綁定紀錄 (如果有重複綁定，資料庫的 UNIQUE 會擋下來或被忽略)
    try:
        data = {
            "parent_id": str(request.parent_id),
            "child_id": str(request.child_id)
        }
        res = supabase.table("family_links").insert(data).execute()
        
        return {"success": True, "message": "綁定成功"}
    except Exception as e:
        # 如果發生 Unique violation，代表已經綁過了
        if "duplicate key value" in str(e) or "UniqueViolation" in str(e) or "23505" in str(e):
            return {"success": True, "message": "已經綁定過了"}
        
        print(f"🚨 Bind Error: {e}")
        raise HTTPException(status_code=500, detail="無法完成綁定，系統發生錯誤。")
# --- 4. 獲取爸爸日總結 (女兒端視角) ---
@router.get("/family-history/{daughter_id}/{target_date}")
async def get_dad_history(daughter_id: str, target_date: date):
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
    start_time = datetime.combine(target_date, datetime.min.time(), tzinfo=TW_TZ).isoformat()
    end_time = datetime.combine(target_date, datetime.max.time(), tzinfo=TW_TZ).isoformat()

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
