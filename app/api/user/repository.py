from sqlalchemy.orm import Session
from app.models.user import User
from uuid import uuid4
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
