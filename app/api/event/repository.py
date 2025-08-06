from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from typing import List, Optional
from app.models.attendance import AttendanceLog, AttendanceReward

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
