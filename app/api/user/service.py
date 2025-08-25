from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.user.repository import insert_user, get_user_by_id, update_user_money, create_transaction
from app.models.moneyTransaction import TransactionDirection
from app.core.exception import CustomException
from uuid import UUID

# 유저 생성(/users/start)
def create_user(db: Session):
    try:
        return insert_user(db)          # repositry.py 의 함수 사용
    except Exception as e:              # 예외 발생 시 400 응답과 메시지 반환
        raise CustomException(message = "서버 내부 오류로 인해 유저를 생성하지 못했습니다.", status = 400)

# 코인 조회(/users/property)
def get_user_property_service(db: Session, user_id: UUID):
    return get_user_by_id(db, user_id)

# 거래 처리(/users/transactions)
def process_transaction(db: Session, user_id: UUID, amount: int, source: str):
    try:
        # 사용자 조회
        user = get_user_by_id(db, user_id)
        if not user:
            raise CustomException(message="사용자를 찾을 수 없습니다.", status=404, code="USER_NOT_FOUND")
        
        # 새로운 잔액 계산
        new_balance = user.money + amount

        print(new_balance)
        
        # 잔액 부족 체크
        if new_balance < 0:
            raise CustomException(
                message=f"잔액이 부족합니다. 현재 잔액: {user.money}원, 요청 금액: {abs(amount)}원", 
                status=400
            )
        
        # 거래 방향 결정
        direction = TransactionDirection.IN if amount > 0 else TransactionDirection.OUT
        
        # 사용자 잔액 업데이트
        updated_user = update_user_money(db, user_id, new_balance)
        
        # 거래 로그 생성
        transaction = create_transaction(db, user_id, amount, source, direction, new_balance)
        
        db.commit()  # 명시적 커밋
        
        return transaction
        
    except CustomException as e:
        db.rollback()
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise CustomException(message="데이터베이스 오류가 발생했습니다.", status=500)
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {str(e)}")
        raise CustomException(message="서버 내부 오류로 인해 거래를 생성하지 못했습니다.", status=500)
