from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# --- 1. 個人檔案相關 (Profiles) ---
class ProfileBase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(dad|daughter)$") # 限制只能是 dad 或 daughter
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    invite_code: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True

# --- 2. 健康紀錄相關 (Health Logs) ---
class HealthLogCreate(BaseModel):
    user_id: UUID
    systolic: int
    diastolic: int
    pulse: int
    period: str # morning/evening

class HealthLogResponse(BaseModel):
    id: int
    user_id: UUID
    systolic: int
    diastolic: int
    pulse: int
    period: str
    created_at: datetime

# --- 3. AI 建議回傳格式 (針對你的 Insight 功能) ---
class DietReference(BaseModel):
    meal_plan: str
    target_calories: int
    protein_g: int

class InsightResponse(BaseModel):
    advice: str
    status: str
    metadata: dict
    diet_reference: DietReference