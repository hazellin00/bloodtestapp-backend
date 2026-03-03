import json
import os
from pathlib import Path
from google import genai
from app.core.config import settings

# Load the static medical reference standard document values to inject as Ground Truth.
def load_health_standards():
    base_path = Path(__file__).resolve().parent.parent.parent.parent
    file_path = base_path / "health_standards.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Initializer for Google GenAI leveraging settings object reading `.env` keys.
client = genai.Client(api_key=settings.gemini_api_key)

async def generate_health_advice(user_profile: dict, daily_logs: list):
    standards = load_health_standards()
    
    # Analyze the input payload dynamically using standard prompt techniques.
    prompt = f"""
    You are an empathetic, caring virtual doctor and personal health assistant designed primarily to analyze blood pressure trends.
    The user reading this is an elderly father, so the tone must be extremely warm, respectful, and easy to understand.
    
    User Profile:
    Age: {user_profile.get("age")}
    Weight: {user_profile.get("weight")} kg
    Height: {user_profile.get("height")} cm
    
    Today's Measurement Logs:
    {daily_logs}
    
    Medical Context (Ground Truth):
    {json.dumps(standards, ensure_ascii=False)}
    
    Instructions:
    1. Base your assessment ONLY on the Ground Truth standards provided.
    2. Write exactly 2 caring sentences summarizing the health trend observed from the day's logs.
    3. Include a specific short "Daily Calorie Goal" estimated by the BMR Mifflin-St Jeor Equation explicitly available in the Ground Truth Context.
    4. Provide the "DASH Veggie/Water portions" specific to the estimated BMR level nearest to the 1600kcal, 2000kcal, or 2400kcal tier.
    5. The final output MUST BE in Traditional Chinese.
    6. Ensure the mandatory medical disclaimer: 'For reference only; consult a physician before adjusting any medication.' is present at the ending footer of your statement.
    """

    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt,
    )
    return response.text
