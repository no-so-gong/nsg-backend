from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from typing import List, Literal, Optional

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

# 동물 상태 상세 조회 응답(/pets/{animalId}) <- 태연: 동물 특정 행동 카테고리 나도 이거 써!
class AnimalInfoResponse(BaseModel):
    animalId: int
    name: str
    userPatternBias: float
    evolutionStage: Literal[1, 2, 3]
    currentEmotion: int
    isRunaway: bool
    status: int    
  
# 가출한 동물 데려오기 응답(/pets/{animalId}/return)
class AnimalEmotionResetResponse(BaseModel):
    message: str
    animal: dict
    money: int
    status: int

# 동물 가출 처리 응답(/pets/{animalId}/runaway)
class AnimalRunawayResponse(BaseModel):
    message: str
    data: dict
    status: int    

