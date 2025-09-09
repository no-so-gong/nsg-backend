from typing import Dict
from pydantic import BaseModel
from typing import Literal

# 행동 
class MLInput(BaseModel):
    current_emotion: int
    action_count: int
    user_pattern_bias: float
    days_since_last_care: int
    animal_type_chick: int
    animal_type_duck: int
    animal_type_shiba: int
    action_feed1: int
    action_feed2: int
    action_feed3: int
    action_play1: int
    action_play2: int
    action_play3: int
    action_gift1: int
    action_gift2: int
    action_gift3: int

class PriceListResponse(BaseModel):
    animalId: int
    evolutionStage: int
    category: str
    prices: Dict[str, int]
    message: str
    status: int

# 감정 메시지 출력
class EmotionMessageRequest(BaseModel):
    predictedDelta: float
    category: Literal["feed", "play", "gift"]

class EmotionMessageResponse(BaseModel):
    message: str
    status: int