from pydantic import BaseModel

class EmotionInput(BaseModel):
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
