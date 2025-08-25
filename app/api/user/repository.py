from sqlalchemy.orm import Session
from app.models.user import User
from app.models.moneyTransaction import MoneyTransaction, TransactionDirection
from uuid import uuid4, UUID
from datetime import datetime
from app.core.config import KST

def insert_user(db: Session) -> User: # 데이터베이스에 유저를 추가하는 쿼리
    # 유저가 이미 하나라도 있으면 새로 생성하지 않음
    # existing_user = db.query(User).first()
    # if existing_user:
    #     return existing_user

    now_kst = datetime.now(KST)

    # 유저가 없으면 새로 생성
    new_user = User(userId=uuid4(), createdAt=now_kst, money=0) # KST 기준으로 DB에 createAt 을 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.userId == user_id).first()

def update_user_money(db: Session, user_id: UUID, new_amount: int) -> User:
    user = db.query(User).filter(User.userId == user_id).first()
    if user:
        user.money = new_amount
        db.flush()  # commit 대신 flush 사용
    return user

def create_transaction(db: Session, user_id: UUID, amount: int, source: str, direction: TransactionDirection, current_money: int) -> MoneyTransaction:
    now_kst = datetime.now(KST)
    
    # txId를 자동 생성 (타임스탬프 기반)
    tx_id = str(int(now_kst.timestamp() * 1000000))
    
    transaction = MoneyTransaction(
        txId=tx_id,
        userId=user_id,
        amount=amount,
        source=source,
        direction=direction,
        currentMoney=current_money,
        createdAt=now_kst
    )
    
    db.add(transaction)
    db.flush()  # commit 대신 flush 사용
    return transaction