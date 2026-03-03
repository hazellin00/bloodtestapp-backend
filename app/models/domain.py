from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime

class RoleEnum(str, Enum):
    dad = "dad"
    daughter = "daughter"

class PeriodEnum(str, Enum):
    morning = "morning"
    evening = "evening"

class Profile(BaseModel):
    id: str # UUID from Supabase Auth
    role: RoleEnum
    family_id: str
    height: Optional[float] = None # cm
    weight: Optional[float] = None # kg
    age: Optional[int] = None

class HealthLog(BaseModel):
    id: Optional[str] = None # UUID
    user_id: str
    systolic: int
    diastolic: int
    heart_rate: int
    period: PeriodEnum
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
