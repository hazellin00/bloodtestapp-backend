from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import supabase

router = APIRouter(tags=["User Profile"])

class UserProfileSchema(BaseModel):
    id: str
    name: str
    age: int
    height: float  # The frontend sends 'height'
    weight: float  # The frontend sends 'weight'
    role: str

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """ 獲取使用者個人資料 """
    res = supabase.table("profiles").select("*").eq("id", user_id).execute()
    
    # Map back to what the frontend expects
    if res.data:
        for p in res.data:
            if "height_cm" in p and p["height_cm"] is not None:
                p["height"] = p.pop("height_cm")
            if "weight_kg" in p and p["weight_kg"] is not None:
                p["weight"] = p.pop("weight_kg")
                
    return res

@router.post("/profile/")
async def save_profile(profile: UserProfileSchema):
    """ 儲存或更新使用者個人資料 """
    
    # 計算 BMI (可選)
    bmi = None
    if profile.height > 0 and profile.weight > 0:
        hm = profile.height / 100
        bmi = round(profile.weight / (hm * hm), 1)

    data = {
        "id": profile.id,
        "name": profile.name,
        "age": profile.age,
        "height_cm": profile.height,  # Map to Supabase column
        "weight_kg": profile.weight,  # Map to Supabase column
        "bmi": bmi,
        "role": profile.role
    }
    
    # 使用 upsert (如果 ID 已存在就更新)
    try:
        res = supabase.table("profiles").upsert(data).execute()
        return res
    except Exception as e:
        print(f"🚨 Save Profile Error: {e}")
        raise HTTPException(status_code=500, detail="無法儲存個人資料到資料庫: " + str(e))
