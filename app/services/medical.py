from typing import Dict, Any

def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """
    計算 BMI 並回傳數值與台灣標準分類
    用於與 Supabase 中的 diet_templates 進行比對
    """
    if height_cm <= 0 or weight_kg <= 0:
        return {"value": 0, "status": "未知"}
    
    height_m = height_cm / 100
    bmi_value = round(weight_kg / (height_m ** 2), 2)
    
    # 採用台灣衛福部標準 (與專案背景相符)
    if bmi_value < 18.5:
        status = "Underweight"
    elif 18.5 <= bmi_value < 24.0:
        status = "Normal"
    elif 24.0 <= bmi_value < 27.0:
        status = "Overweight"
    else:
        status = "Obese"
        
    return {
        "value": bmi_value,
        "status": status
    }

def get_bp_category(systolic: int, diastolic: int) -> str:
    """
    判定血壓等級。
    注意：此處字串須與你清理資料時產生的 'bp_category' 欄位完全一致 (High, Elevated, Normal)
    """
    if systolic >= 140 or diastolic >= 90:
        return "High"
    elif systolic >= 120 or diastolic >= 80:
        return "Elevated"
    else:
        return "Normal"

def calculate_bmr(weight_kg: float, height_cm: float, age_years: int, gender: str = "male") -> float:
    """
    計算基礎代謝率 (BMR) - 使用 Mifflin-St Jeor 公式
    這可以作為 AI 提供熱量建議時的科學參考底稿
    """
    if weight_kg <= 0 or height_cm <= 0 or age_years <= 0:
        return 0.0
    
    # 公式基準：(10 * 體重) + (6.25 * 身高) - (5 * 年齡)
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years)
    
    if gender.lower() == "male":
        return bmr + 5
    else:
        return bmr - 161

# 如果你仍想保留部分靜態建議作為「無資料庫回傳時」的備案，可以保留此函式
def get_fallback_diet_servings(bmr: float) -> Dict[str, str]:
    """
    當資料庫查詢失敗時的備用建議
    """
    if bmr < 1800:
        return {"tier": "1600_kcal", "veg": "3 份", "fruit": "2 份"}
    elif bmr < 2200:
        return {"tier": "2000_kcal", "veg": "4 份", "fruit": "3 份"}
    else:
        return {"tier": "2400_kcal", "veg": "5 份", "fruit": "4 份"}