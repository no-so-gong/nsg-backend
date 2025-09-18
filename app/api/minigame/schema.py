from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class MinigameStartResponse(BaseModel):
    message: str
    data: dict
    status: int

class MinigameResultRequest(BaseModel):
    score: Optional[int] = None
    money: Optional[int] = None
    timeSpent: Optional[int] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None

    @field_validator('score', 'money', 'timeSpent')
    @classmethod
    def validate_non_negative(cls, v):
        # null 값은 허용, 값이 있을 때만 검증
        if v is not None and v < 0:
            raise ValueError('값은 0 이상이어야 합니다')
        return v

    @model_validator(mode='after')
    def validate_completion_time(self):
        # 둘 다 값이 있을 때만 시간 순서 검증
        if self.completedAt is not None and self.startedAt is not None:
            if self.completedAt <= self.startedAt:
                raise ValueError('completedAt은 startedAt보다 이후 시각이어야 합니다')
        return self

class MinigameResultData(BaseModel):
    startedAt: Optional[datetime]
    completedAt: Optional[datetime]
    score: Optional[int]
    timeSpent: Optional[int]
    money: Optional[int]
    gameId: int

class MinigameResultResponse(BaseModel):
    status: int
    message: str
    data: dict[str, MinigameResultData]

    class Config:
        from_attributes = True