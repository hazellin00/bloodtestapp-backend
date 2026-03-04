from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np
from app.database import supabase  # 確保你 app/database.py 有定義好 supabase client
from app.services.ai import generate_health_advice
from app.services.medical import calculate_bmi, get_bp_category

router = APIRouter()

# 定義更精確的請求格式
class InsightRequest(BaseModel):
    user_id: str
    weight: float
    height: float
    age: int
    systolic: int
    diastolic: int

@router.post("/")
async def get_insights(request: InsightRequest):
    """
    結合用戶即時數據與 Supabase (Kaggle 資料集) 產生個性化健康建議。
    """
    try:
        # 1. 使用 medical.py 計算基礎數值
        bmi_info = calculate_bmi(request.weight, request.height)
        bmi_value = bmi_info["value"]
        bp_status = get_bp_category(request.systolic, request.diastolic)

        # 2. 從 Supabase diet_templates 撈取符合血壓等級的資料
        # 我們撈出前 20 筆，然後在 Python 端找 BMI 最接近的
        response = supabase.table("diet_templates") \
            .select("*") \
            .eq("bp_category", bp_status) \
            .limit(20) \
            .execute()

        templates = response.data

        if not templates:
            # 如果資料庫剛好沒資料，給一個基礎預設值
            best_template = {
                "recommended_meal_plan": "均衡飲食，減少鈉鹽攝取",
                "recommended_calories": 2000,
                "recommended_protein": 70,
                "recommended_carbs": 250
            }
        else:
            # 3. 演算法：尋找與用戶 BMI 差距最小的那一筆 Kaggle 紀錄
            # 確保 bmi 欄位轉換為 float 進行比對
            best_template = min(
                templates, 
                key=lambda x: abs(float(x.get('bmi', 0)) - bmi_value)
            )

        # 4. 準備給 AI 的上下文
        user_profile = {
            "age": request.age,
            "bmi_status": bmi_info["status"],
            "bmi": bmi_value
        }
        daily_logs = f"收縮壓:{request.systolic} / 舒張壓:{request.diastolic}"

        # 5. 呼叫 ai.py 讓 Gemini 產生暖心建議 (傳入 best_template)
        advice_text = await generate_health_advice(user_profile, daily_logs, best_template)

        # 6. 回傳結果給前端
        return {
            "advice": advice_text,
            "status": "success",
            "metadata": {
                "bmi": bmi_value,
                "bp_level": bp_status,
                "source": "Kaggle Personalized Diet Dataset"
            },
            "diet_reference": {
                "meal_plan": best_template.get("recommended_meal_plan"),
                "target_calories": best_template.get("recommended_calories"),
                "protein_g": best_template.get("recommended_protein")
            }
        }

    except Exception as e:
        print(f"Insight Error: {e}")
        raise HTTPException(status_code=500, detail="分析數據時發生錯誤")