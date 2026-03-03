import json
import os
from pathlib import Path
import google.generativeai as genai
from app.core.config import settings

# 1. 穩定版初始化方式
genai.configure(api_key=settings.gemini_api_key)
# 建議使用 gemini-1.5-flash，速度快且免費額度高
model = genai.GenerativeModel('gemini-1.5-flash')

def load_health_standards():
    """載入健康標準 JSON"""
    # 根據您的檔案結構動態找尋 health_standards.json
    base_path = Path(__file__).resolve().parent.parent.parent
    file_path = base_path / "health_standards.json"
    
    # 檢查檔案是否存在，避免報錯
    if not file_path.exists():
        return {"error": "標準檔案不存在"}
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def generate_health_advice(user_profile: dict, daily_logs: list):
    standards = load_health_standards()
    
    # 這裡保留您原本精美的 Prompt 邏輯
    prompt = f"""
    你是一位充滿同理心、關懷家人的虛擬醫生和個人健康助手，專門分析血壓趨勢。
    閱讀這份建議的是一位年邁的父親，因此語氣必須極其溫暖、尊重且易於理解。
    
    用戶資料：
    年齡: {user_profile.get("age")}
    體重: {user_profile.get("weight")} 公斤
    身高: {user_profile.get("height")} 公分
    
    今日測量紀錄：
    {daily_logs}
    
    醫療背景參考（基準值）：
    {json.dumps(standards, ensure_ascii=False)}
    
    指令：
    1. 僅根據提供的基準值標準進行評估。
    2. 寫下正好 2 句關懷的話，總結從今日日誌中觀察到的健康趨勢。
    3. 包含一個具體的短「每日卡路里目標」，根據基準值中的 Mifflin-St Jeor 公式估算。
    4. 根據估算的 BMR 水平（最接近 1600/2000/2400kcal 等級），提供特定的「DASH 蔬果/飲水份量」。
    5. 最終輸出必須使用繁體中文。
    6. 必須包含強制性醫療免責聲明：'僅供參考；在調整任何藥物之前，請務必諮詢醫師。' 放在結尾處。
    """

    try:
        # 2. 穩定版呼叫方式
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI 生成失敗: {e}")
        return "暫時無法生成建議。請保持心情愉快，並定時量測血壓。僅供參考；在調整任何藥物之前，請務必諮詢醫師。"