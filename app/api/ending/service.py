from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exception import CustomException
from app.api.ending.repository import get_user_by_id, delete_user_and_related_data


def reset_game_service(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)
    if not user:
        raise CustomException(message="존재하지 않는 사용자입니다.", status=404)

    try:
        delete_user_and_related_data(db, user_id)
    except Exception:
        db.rollback()
        raise

    # 초기 상태 반환 스펙
    return {
        "money": 0,
        "animals": [
            {"animalId": 1, "name": None, "current_emotion": 50, "isRunaway": False},
            {"animalId": 2, "name": None, "current_emotion": 50, "isRunaway": False},
            {"animalId": 3, "name": None, "current_emotion": 50, "isRunaway": False},
        ],
        "totalPlayDays": 0,
        "totalUsedMoney": 0,
    }
