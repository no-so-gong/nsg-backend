from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exception import CustomException
from app.api.ending.repository import (
    get_user_by_id,
    delete_user_and_related_data,
    get_ending_summary_data,
    check_all_animals_happy
)


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


def get_ending_summary_service(db: Session, user_id: UUID):
    user = get_user_by_id(db, user_id)
    if not user:
        raise CustomException(message="존재하지 않는 사용자입니다.", status=404)

    # 세 마리 동물 모두 감정도 100인지 확인
    if not check_all_animals_happy(db, user_id):
        raise CustomException(message="아직 게임이 종료되지 않았습니다. 모든 동물의 감정도가 100이 되어야 합니다.", status=400)

    # 요약 데이터 조회
    summary_data = get_ending_summary_data(db, user_id)

    return {
        **summary_data,
        "message": "게임 요약 정보 조회 성공"
    }
