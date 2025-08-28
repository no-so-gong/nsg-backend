from fastapi import APIRouter
from app.api.care.schema import MLInput
from app.api.care.service import predict_emotion

router = APIRouter(prefix="/api/v1/cares", tags=["Care"])

@router.post("/action") # 기존 /predict 테스트 api 이름만 변경함. 이후에 작업 다시
def get_emotion_prediction(input_data: MLInput):
    predicted_delta = predict_emotion(input_data)
    return {
        "predicted_emotion_delta": predicted_delta
    }
