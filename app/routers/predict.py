from fastapi import APIRouter
from app.schemas.input import EmotionInput
from app.services.predictor import predict_emotion

router = APIRouter()

@router.post("/predict")
def get_emotion_prediction(input_data: EmotionInput):
    predicted_delta = predict_emotion(input_data)
    return {
        "predicted_emotion_delta": predicted_delta
    }
