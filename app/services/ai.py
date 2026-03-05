import os
from google import genai
from app.core.config import settings

api_key = settings.gemini_api_key
client = genai.Client(api_key=api_key)

async def generate_health_advice(user_profile: dict, daily_logs: str, template_data: dict = None):
    """
    通用 AI 建議生成器
    """
    # 確保 template_data 不為 None 以免字典讀取噴錯
    tpl = template_data or {}
    
    prompt = f"""
    你是一位充滿同理心的家庭醫生。請分析以下數據並給予建議。
    
    用戶資料：{user_profile.get("age")}歲, BMI: {user_profile.get("bmi")}
    今日血壓：{daily_logs}
    
    根據專業數據庫匹配的建議模板：
    - 推薦飲食：{tpl.get("recommended_meal_plan", "均衡飲食")}
    - 建議熱量：{tpl.get("recommended_calories", 2000)} kcal
    - 建議營養比例：蛋白質 {tpl.get("recommended_protein", 60)}g, 碳水 {tpl.get("recommended_carbs", 250)}g
    
    請遵守以下規範：
    1. 用溫暖、關懷年長者的語氣寫 2 句健康趨勢總結。
    2. 將上述「推薦飲食」與「建議熱量」自然地融入建議中。
    3. 最終輸出必須使用繁體中文。
    4. 結尾必須包含：'僅供參考；在調整任何藥物之前，請務必諮詢醫師。'
    """

    try:
        # 使用更穩定的模型版本 (2.0 flash 或 1.5 flash)
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"🚨 AI 生成錯誤: {e}")
        # 針對 503 或是 API 繁忙的親切回傳
        if "503" in str(e):
            return "爸爸，AI 醫師現在有點忙，但您的血壓數據已經安全存好了！記得多喝水、早點休息。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"
        return "爸爸，今天的數據已經幫你存好了。記得保持心情輕鬆，並按時服藥喔。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"