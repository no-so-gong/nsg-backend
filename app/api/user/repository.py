from sqlalchemy.orm import Session
from app.models.user import User
from uuid import uuid4
from datetime import datetime

def insert_user(db: Session) -> User: # 데이터베이스에 유저를 추가하는 쿼리
     # 유저가 이미 하나라도 있으면 새로 생성하지 않음
    existing_user = db.query(User).first()
    if existing_user:
        return existing_user

    # 유저가 없으면 새로 생성
    new_user = User(userId=uuid4(), createdAt=datetime.utcnow(), money=0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
