from fastapi import APIRouter, HTTPException, Depends
from datetime import date, datetime
from typing import List
import os
from ..database import supabase  # 假設您已配置好 supabase client
import google.generativeai as genai

router = APIRouter(prefix="/history", tags=["Calendar History"])

# 配置 Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@router.get("/{user_id}/{target_date}")
async def get_daily_summary(user_id: str, target_date: date):
    """
    獲取爸爸特定日期的血壓紀錄與 AI 總結
    target_date 格式: YYYY-MM-DD
    """
    # 1. 從 Supabase 抓取當天的紀錄
    # 這裡搜尋 created_at 在 target_date 的 00:00 到 23:59 之間
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
        return {"date": target_date, "logs": [], "summary": "當天沒有紀錄喔，記得提醒爸爸量血壓！"}

    # 2. 整理數據給 Gemini
    log_summary = "\n".join([
        f"時段: {l['period']}, 血壓: {l['systolic']}/{l['diastolic']}, 心率: {l['heart_rate']}"
        for l in logs
    ])

    # 3. 呼叫 Gemini 生成「暖心回顧」
    prompt = f"""
    我父親在 {target_date} 的血壓紀錄如下：
    {log_summary}
    請根據這些數據，寫一段 2 句話的中文暖心回顧。
    如果是正常的，請給予鼓勵；如果偏高，請溫柔提醒。
    最後必須加上免責聲明：『僅供參考；調整藥物前請務必諮詢醫師。』
    """
    
    try:
        ai_response = model.generate_content(prompt)
        summary = ai_response.text
    except Exception:
        summary = "當天數據已存檔，請參考上方數值。"

    return {
        "date": target_date,
        "logs": logs,
        "summary": summary
    }