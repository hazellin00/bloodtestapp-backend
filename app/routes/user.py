from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import supabase

router = APIRouter(tags=["User Profile"])

class UserProfileSchema(BaseModel):
    id: str
    name: str
    age: int
    height: float
    weight: float
    role: str

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """ 獲取使用者個人資料 """
    res = supabase.table("profiles").select("*").eq("id", user_id).execute()
    return res

@router.post("/profile/")
async def save_profile(profile: UserProfileSchema):
    """ 儲存或更新使用者個人資料 """
    data = {
        "id": profile.id,
        "name": profile.name,
        "age": profile.age,
        "height": profile.height,
        "weight": profile.weight,
        "role": profile.role
    }
    
    # 使用 upsert (如果 ID 已存在就更新)
    try:
        res = supabase.table("profiles").upsert(data).execute()
        return res
    except Exception as e:
        print(f"🚨 Save Profile Error: {e}")
        raise HTTPException(status_code=500, detail="無法儲存個人資料到資料庫")
