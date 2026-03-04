# app/services/ai.py
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_health_advice(user_profile: dict, daily_logs: list, template_data: dict):
    """
    template_data: 從 Supabase diet_templates 撈出來的匹配資料
    """
    prompt = f"""
    你是一位充滿同理心的家庭醫生。請分析以下數據並給予建議。
    
    用戶資料：{user_profile.get("age")}歲, BMI: {user_profile.get("bmi")}
    今日血壓：{daily_logs}
    
    根據專業數據庫匹配的建議模板：
    - 推薦飲食：{template_data.get("recommended_meal_plan")}
    - 建議熱量：{template_data.get("recommended_calories")} kcal
    - 建議營養比例：蛋白質 {template_data.get("recommended_protein")}g, 碳水 {template_data.get("recommended_carbs")}g
    
    請遵守以下規範：
    1. 用溫暖、關懷年長者的語氣寫 2 句健康趨勢總結。
    2. 將上述「推薦飲食」與「建議熱量」自然地融入建議中。
    3. 最終輸出必須使用繁體中文。
    4. 結尾必須包含：'僅供參考；在調整任何藥物之前，請務必諮詢醫師。'
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "保持心情愉快，並定時量測血壓。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"