from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.models.user import User
from app.models.animal import Animal
from app.models.moneyTransaction import MoneyTransaction
from app.models.attendance import AttendanceLog
from app.models.birthday import BirthdayReward


def delete_user_and_related_data(db: Session, user_id: UUID):
    # 연관 데이터 삭제 (동물, 트랜잭션, 출석, 생일 보상, 유저)
    db.execute(delete(Animal).where(Animal.userId == user_id))
    db.execute(delete(MoneyTransaction).where(MoneyTransaction.userId == user_id))
    db.execute(delete(AttendanceLog).where(AttendanceLog.userId == user_id))
    db.execute(delete(BirthdayReward).where(BirthdayReward.userId == user_id))
    db.execute(delete(User).where(User.userId == user_id))
    db.commit()


def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.userId == user_id).first()
