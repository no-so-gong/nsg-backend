from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import delete, func, distinct

from app.models.user import User
from app.models.animal import Animal
from app.models.moneyTransaction import MoneyTransaction, TransactionDirection
from app.models.attendance import AttendanceLog
from app.models.birthday import BirthdayReward
from app.models.minigameattempts import MinigameAttempt
from app.models.userminigameplays import UserMinigamePlay
from app.models.action_log import ActionLog

def delete_user_and_related_data(db: Session, user_id: UUID):
    # 미니게임 관련 데이터 삭제
    db.execute(delete(MinigameAttempt).where(MinigameAttempt.userId == user_id))
    db.execute(delete(UserMinigamePlay).where(UserMinigamePlay.userId == user_id))

    # 케어 로그 삭제
    db.execute(delete(ActionLog).where(ActionLog.userId == user_id))

    # 연관 데이터 삭제 (동물, 트랜잭션, 출석, 생일 보상)
    db.execute(delete(Animal).where(Animal.userId == user_id))
    db.execute(delete(MoneyTransaction).where(MoneyTransaction.userId == user_id))
    db.execute(delete(AttendanceLog).where(AttendanceLog.userId == user_id))
    db.execute(delete(BirthdayReward).where(BirthdayReward.userId == user_id))

    # 마지막으로 유저 삭제
    db.execute(delete(User).where(User.userId == user_id))
    db.commit()


def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.userId == user_id).first()


def get_ending_summary_data(db: Session, user_id: UUID):
    # 총 플레이 일수 (출석 로그의 고유 날짜 수)
    total_play_days = db.query(func.count(distinct(AttendanceLog.date))).filter(
        AttendanceLog.userId == user_id
    ).scalar() or 0

    # 총 사용 금액 (direction이 'out'인 트랜잭션의 합계)
    total_used_money = db.query(func.sum(MoneyTransaction.amount)).filter(
        MoneyTransaction.userId == user_id,
        MoneyTransaction.direction == TransactionDirection.OUT
    ).scalar() or 0

    # 연속 출석일 계산 (가장 최근 날짜부터 역순으로 연속된 날짜 수 계산)
    attendance_dates = db.query(distinct(AttendanceLog.date)).filter(
        AttendanceLog.userId == user_id
    ).order_by(AttendanceLog.date.desc()).all()

    consecutive_days = 0
    if attendance_dates:
        from datetime import timedelta
        prev_date = None
        for (date,) in attendance_dates:
            if prev_date is None:
                consecutive_days = 1
                prev_date = date
            elif prev_date - date == timedelta(days=1):
                consecutive_days += 1
                prev_date = date
            else:
                break

    # 가출 횟수 (모든 동물의 누적 가출 횟수 합계)
    runaway_count = db.query(func.sum(Animal.runawayCount)).filter(
        Animal.userId == user_id
    ).scalar() or 0

    return {
        "totalPlayDays": total_play_days,
        "totalUsedMoney": total_used_money,
        "consecutiveAttendanceDays": consecutive_days,
        "runawayCount": runaway_count
    }


def check_all_animals_happy(db: Session, user_id: UUID):
    # 세 마리의 동물이 모두 currentEmotion이 100인지 확인
    animals = db.query(Animal).filter(Animal.userId == user_id).all()

    if len(animals) != 3:
        return False

    return all(float(animal.currentEmotion) == 100.0 for animal in animals)
