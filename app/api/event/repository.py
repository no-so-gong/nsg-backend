from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from typing import List, Optional
from app.models.attendance import AttendanceLog, AttendanceReward
from app.models.birthday import BirthdayReward, Animal

def get_attendance_logs(db: Session, user_id: UUID) -> List[AttendanceLog]:
    return db.query(AttendanceLog).filter(AttendanceLog.userId == user_id).all()

def get_today_attendance_log(db: Session, user_id: UUID, today: date) -> Optional[AttendanceLog]:
    return db.query(AttendanceLog).filter(
        AttendanceLog.userId == user_id,
        AttendanceLog.date == today
    ).first()

def get_attendance_rewards(db: Session) -> List[AttendanceReward]:
    return db.query(AttendanceReward).order_by(AttendanceReward.attendanceRewardId).all()

def get_reward_by_index(db: Session, index: int) -> Optional[AttendanceReward]:
    return db.query(AttendanceReward).filter(
        AttendanceReward.attendanceRewardId == index
    ).first()

def save_attendance_log(db: Session, log: AttendanceLog) -> None:
    db.add(log)

def commit_db(db: Session) -> None:
    db.commit()

# 생일
def get_birthday_animal_by_user_and_date(db: Session, user_id: UUID, today: date) -> Optional[Animal]:
    return db.query(Animal).filter(
        Animal.userId == user_id,
        Animal.birthday == today
    ).first()

def has_birthday_reward_been_given(db: Session, user_id: UUID, animal_id: int, today: date) -> bool:
    exists = db.query(BirthdayReward).filter(
        BirthdayReward.userId == user_id,
        BirthdayReward.animalId == animal_id,
        BirthdayReward.date == today
    ).first()
    return exists is not None

def save_birthday_reward(db: Session, reward: BirthdayReward) -> None:
    db.add(reward)

def get_birthday_animals_by_user_and_date(db: Session, user_id: UUID, today: date) -> List[Animal]:
    return db.query(Animal).filter(
        Animal.userId == user_id,
        Animal.birthday == today
    ).all()