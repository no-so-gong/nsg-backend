from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

# 동물의 id, 이름의 포멧
class AnimalNicknameRequestItem(BaseModel):
    animalId: int = Field(..., ge=1, le=3) # 1~3 범위의 ID만 허용
    name: str = Field(..., max_length=10) # 최대 10자까지 입력 허용

# 동물 이름 지어주기 요청(/pets/nickname)
class AnimalNicknameRequest(BaseModel):
    animals: List[AnimalNicknameRequestItem]

# 동물 이름 지어주기 응답(/pets/nickname)
class AnimalNicknameResponse(BaseModel):
    message: str
    data: dict
    status: int
