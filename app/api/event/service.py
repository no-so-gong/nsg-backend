from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
from app.api.event.schema import AttendanceResponseData, Reward, BoardItem
from app.core.exception import CustomException
from app.models.attendance import AttendanceReward
from app.api.event import repository
from app.api.user.service import process_transaction

# 출석 보상 조회(/events/attendance)
def get_attendance_data(user_id: UUID, db: Session) -> AttendanceResponseData:
    today = date.today()
    logs = repository.get_attendance_logs(db, user_id)
    rewards = repository.get_attendance_rewards(db)

    total_attendance = len(logs)
    already_checked_in = any(log.date == today for log in logs)
    today_index = ((total_attendance - 1) % 7) + 1

    today_reward_row = next((r for r in rewards if r.attendanceRewardId == today_index), None)
    today_reward = Reward(
        type=today_reward_row.rewardType,
        amount=today_reward_row.rewardAmount
    ) if today_reward_row else Reward(type="money", amount=0)

    checked_day_ids = {log.attendanceRewardId for log in logs}
    board = [
        BoardItem(
            day=reward.attendanceRewardId,
            reward=reward.rewardAmount,
            checkedIn=reward.attendanceRewardId in checked_day_ids
        )
        for reward in rewards
    ]

    return AttendanceResponseData(
        alreadyCheckedIn=already_checked_in,
        totalAttendance=total_attendance,
        todayIndex=today_index,
        todayReward=today_reward,
        board=board
    )

# 출석 보상 받기(/events/attendance/checkin)
def check_in_attendance(user_id: UUID, db: Session) -> AttendanceResponseData:
    today = date.today()

    if repository.get_today_attendance_log(db, user_id, today):
        raise CustomException(message="이미 오늘 출석하셨습니다.", status=409)

    # 누적 출석 수 계산 (기존 로그 수)
    logs = repository.get_attendance_logs(db, user_id)
    total_attendance = len(logs) + 1  # 오늘 포함
    today_index = ((total_attendance - 1) % 7) + 1

    reward_row = repository.get_reward_by_index(db, today_index)
    if not reward_row:
        reward_row = AttendanceReward(attendanceRewardId=today_index, rewardAmount=0, rewardType="money")

    try:
        new_log = repository.create_and_save_attendance_log(db, user_id, today, reward_row.attendanceRewardId)
        
        # 유저 보상 지급 처리
        process_transaction(db, user_id, reward_row.rewardAmount, "attendance", commit=False)
        
        db.commit()
    except Exception:
        db.rollback()
        raise

    all_logs = logs + [new_log]
    checked_day_ids = {log.attendanceRewardId for log in all_logs}
    rewards = repository.get_attendance_rewards(db)

    board = [
        BoardItem(
            day=reward.attendanceRewardId,
            reward=reward.rewardAmount,
            checkedIn=reward.attendanceRewardId in checked_day_ids
        )
        for reward in rewards
    ]

    return AttendanceResponseData(
        alreadyCheckedIn=False,
        totalAttendance=total_attendance,
        todayIndex=today_index,
        todayReward=Reward(type=reward_row.rewardType, amount=reward_row.rewardAmount),
        board=board
    )

# 생일 축하 선물 받기(/events/birthday/reward)
def give_birthday_reward(user_id: UUID, today: date, db: Session):
    animal = repository.get_birthday_animal_by_user_and_date(db, user_id, today)
    if not animal:
        raise CustomException(message="오늘 생일이 아님", status=403)

    if repository.has_birthday_reward_been_given(db, user_id, animal.animalId, today):
        raise CustomException(message="이미 선물 수령함", status=409)

    REWARD_AMOUNT = 100
    REWARD_TYPE = "money"

    try:
        birthday_reward = repository.create_and_save_birthday_reward(db, user_id, animal.animalId, today)
        
        # 유저 머니 업데이트
        process_transaction(db, user_id, REWARD_AMOUNT, "birthday", commit=False) 
        
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "animal_id": animal.animalId,
        "name": animal.name,
        "rewarded": True,
        "reward": {
            "type": REWARD_TYPE,
            "amount": REWARD_AMOUNT
        }
    }
    
# 오늘 생일인 동물 조회(/events/birthday)
def get_birthday_animals(user_id: UUID, today: date, db: Session):
    animals = repository.get_birthday_animals_by_user_and_date(db, user_id, today)
    return [
        {
            "animalId": a.animalId,
            "name": a.name,
            "rewarded": repository.has_birthday_reward_been_given(db, user_id, a.animalId, today)
        }
        for a in animals
    ]
