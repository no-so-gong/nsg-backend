from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.care.schema import MLInput, PriceListResponse
from app.api.care.service import predict_emotion, get_price_list_service
from app.core.database import get_db
from app.core.exception import CustomException

router = APIRouter(prefix="/api/v1/cares", tags=["Care"])

@router.post("/action") # 기존 /predict 테스트 api 이름만 변경함. 이후에 작업 다시
def get_emotion_prediction(input_data: MLInput):
    predicted_delta = predict_emotion(input_data)
    return {
        "predicted_emotion_delta": predicted_delta
    }

@router.get("/pricelist", response_model=PriceListResponse)
def get_price_list(
    category: str = Query(..., description="행동 카테고리 (feed, play, gift)"),
    animalId: int = Query(..., description="동물 ID"),
    db: Session = Depends(get_db),
    user_id: UUID = Header(..., alias="user-id")
):
    try:
        return get_price_list_service(db, category, animalId, user_id)
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message="서버 내부 오류가 발생했습니다.", status=500)
