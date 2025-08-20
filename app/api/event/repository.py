from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from typing import List, Optional
from app.models.attendance import AttendanceLog, AttendanceReward
from app.models.birthday import BirthdayReward
from app.models.animal import Animal
from sqlalchemy import extract

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

def create_and_save_attendance_log(db: Session, user_id: UUID, today: date, reward_id: int) -> AttendanceLog:
    log = AttendanceLog(
        date=today,
        userId=user_id,
        attendanceRewardId=reward_id
    )
    db.add(log)
    return log

def save_attendance_log(db: Session, log: AttendanceLog) -> None:
    db.add(log)

# 오늘 생일인 동물 하나 조회
def get_birthday_animal_by_user_and_date(db: Session, user_id: UUID, today: date) -> Optional[Animal]:
    return db.query(Animal).filter(
        Animal.userId == user_id,
        extract("month", Animal.birthday) == today.month,
        extract("day", Animal.birthday) == today.day
        # extract("month", Animal.birthday) == 4,
        # extract("day", Animal.birthday) == 19
    ).first()

# 오늘 생일인 모든 동물 조회 (수정 완료)
def get_birthday_animals_by_user_and_date(db: Session, user_id: UUID, today: date) -> List[Animal]:
    return db.query(Animal).filter(
        Animal.userId == user_id,
        extract("month", Animal.birthday) == today.month,
        extract("day", Animal.birthday) == today.day
        # extract("month", Animal.birthday) == 4,
        # extract("day", Animal.birthday) == 19
    ).all()

# 오늘 생일 보상 지급 여부 확인
def has_birthday_reward_been_given(db: Session, user_id: UUID, animal_id: int, today: date) -> bool:
    exists = db.query(BirthdayReward).filter(
        BirthdayReward.userId == user_id,
        BirthdayReward.animalId == animal_id,
        BirthdayReward.date == today
    ).first()
    return exists is not None

# 생일 보상 기록 저장
def create_and_save_birthday_reward(db: Session, user_id: UUID, animal_id: int, today: date) -> BirthdayReward:
    reward = BirthdayReward(
        date=today,
        userId=user_id,
        animalId=animal_id
    )
    db.add(reward)
    return reward

def save_birthday_reward(db: Session, reward: BirthdayReward) -> None:
    db.add(reward)