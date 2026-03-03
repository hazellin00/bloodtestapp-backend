import json
from pathlib import Path
from typing import Dict, Any

def get_health_standards() -> Dict[str, Any]:
    base_path = Path(__file__).resolve().parent.parent.parent.parent
    file_path = base_path / "health_standards.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_bmi(weight_kg: float, height_cm: float) -> str:
    """Calculates BMI and returns the WHO category."""
    if height_cm <= 0 or weight_kg <= 0:
         return "Invalid input"
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    # WHO BMI: <18.5 (Underweight), 18.5-24.9 (Normal), 25-29.9 (Overweight), >=30 (Obese)
    # Aligning with Taiwanese BMI standard as per prompt context: >27 Obese, 24-27 Overweight, 18.5-24 Normal, <18.5 Underweight
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.0:
        return "Normal"
    elif 24.0 <= bmi < 27.0:
        return "Overweight"
    else:
        return "Obese"

def calculate_bmr(weight_kg: float, height_cm: float, age_years: int) -> float:
    """Calculates BMR using the Mifflin-St Jeor Equation for males (+5)."""
    if weight_kg <= 0 or height_cm <= 0 or age_years <= 0:
        return 0.0
    # Formula: (10 * weight) + (6.25 * height) - (5 * age) + 5
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + 5
    return bmr

def get_dash_diet_recommendation(bmr: float) -> Dict[str, str]:
    """Provides scaled DASH diet servings based on calculated BMR."""
    standards = get_health_standards()
    dash_categories = standards.get("dash_diet", {}).get("categories", {})
    
    # Match BMR nearest to the 1600kcal, 2000kcal, or 2400kcal tier
    if bmr < 1800:
        tier = "1600_kcal"
    elif bmr < 2200:
        tier = "2000_kcal"
    else:
        tier = "2400_kcal"
        
    return dash_categories.get(tier, {})
