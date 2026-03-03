from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.domain import Profile, HealthLog
from app.services.ai import generate_health_advice
from app.services.medical import calculate_bmi, calculate_bmr, get_dash_diet_recommendation

router = APIRouter()

class InsightRequest(BaseModel):
    user_profile: Dict[str, Any]
    daily_logs: List[Dict[str, Any]]

@router.post("/")
async def get_insights(request: InsightRequest):
    """
    Combines the user profile and daily health logs to generate personalized
    health advice using Google Gemini and baseline formula parameters.
    """
    profile_data = request.user_profile
    logs_data = request.daily_logs
    
    # Check if necessary data for Medical calculations exists
    weight = profile_data.get("weight", 0)
    height = profile_data.get("height", 0)
    age = profile_data.get("age", 0)
    
    # Supplement context variables
    calculated_data = {}
    if weight and height and age:
        bmi_status = calculate_bmi(weight, height)
        bmr = calculate_bmr(weight, height, age)
        dash_diet = get_dash_diet_recommendation(bmr)
        
        calculated_data = {
            "bmi_category": bmi_status,
            "estimated_bmr": bmr,
            "dash_diet_servings": dash_diet
        }
        # Injects these computed baselines into the profile prompt dictionary
        profile_data["Calculated Ground Truth Context"] = calculated_data
        
    try:
        advice_text = await generate_health_advice(profile_data, logs_data)
        return {
            "advice": advice_text,
            "medical_baselines": calculated_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
