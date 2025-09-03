from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.care.schema import PriceListResponse, CareActionRequest, CareActionResponse
from app.api.care.service import get_price_list_service, predict_and_apply_emotion_change, daily_increment_days_since_care_service
from app.core.database import get_db
from app.core.exception import CustomException

router = APIRouter(prefix="/api/v1/cares", tags=["Care"])

@router.post("/action", response_model=CareActionResponse)
def perform_care_action(
    request: CareActionRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Header(..., alias="user-id")
):
    # CareLogs 시스템에 따른 케어 행동 수행 API
    try:
        result = predict_and_apply_emotion_change(
            db, 
            user_id, 
            request.animal_id, 
            request.action_id
        )
        return result
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message="서버 내부 오류가 발생했습니다.", status=500)

@router.post("/batch/daily-increment")
def daily_increment_days_since_care(
    db: Session = Depends(get_db)
):
    # 자정 배치용 - 모든 동물의 마지막 케어 이후 경과일 +1 증가
    try:
        result = daily_increment_days_since_care_service(db)
        return result
    except CustomException as e:
        raise e
    except Exception as e:
        raise CustomException(message="서버 내부 오류가 발생했습니다.", status=500)

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
