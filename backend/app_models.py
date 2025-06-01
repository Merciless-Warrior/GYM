from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 👤 Користувач
class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str
    password: str
    role: str = "user"

# 🏋️ Результат тренування
class WorkoutResultModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    exercise: str
    value: int
    date: datetime = Field(default_factory=datetime.utcnow)
