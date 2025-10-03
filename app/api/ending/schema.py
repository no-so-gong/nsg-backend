from pydantic import BaseModel
from typing import List, Optional


class AnimalResetInfo(BaseModel):
    animalId: int
    name: Optional[str]
    current_emotion: int
    isRunaway: bool


class ResetResponse(BaseModel):
    message: str
    money: int
    animals: List[AnimalResetInfo]
    totalPlayDays: int
    totalUsedMoney: int
    status: int


class EndingSummaryResponse(BaseModel):
    totalPlayDays: int
    totalUsedMoney: int
    consecutiveAttendanceDays: int
    runawayCount: int
    message: str
    status: int
