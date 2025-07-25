from sqlalchemy.orm import Session
from app.api.user.repository import insert_user
from app.core.exception import CustomException

# 유저 생성(/users/start)
def create_user(db: Session):
    try:
        return insert_user(db)          # repositry.py 의 함수 사용
    except Exception as e:              # 예외 발생 시 400 응답과 메시지 반환
        raise CustomException(message = "서버 내부 오류로 인해 유저를 생성하지 못했습니다.", status = 400)

