from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
from app.api.event.schema import AttendanceResponseData, Reward, BoardItem
from app.core.exception import CustomException
from app.models.attendance import AttendanceLog, AttendanceReward
from app.api.event import repository

# 출석 보상 조회(/event/attendance)
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

# 출석 보상 받기(/event/attendance/checkin)
def check_in_attendance(user_id: UUID, db: Session) -> AttendanceResponseData:
    today = date.today()

    if repository.get_today_attendance_log(db, user_id, today):
        raise CustomException(message="이미 오늘 출석하셨습니다.", status=409)

    # 누적 출석 수 계산 (기존 로그 수)
    logs = db.query(AttendanceLog).filter(AttendanceLog.userId == user_id).all()
    total_attendance = len(logs) + 1  # 오늘 포함
    today_index = ((total_attendance - 1) % 7) + 1

    reward_row = repository.get_reward_by_index(db, today_index)
    if not reward_row:
        reward_row = AttendanceReward(attendanceRewardId=today_index, rewardAmount=0, rewardType="money")

    new_log = AttendanceLog(
        date=today,
        userId=user_id,
        attendanceRewardId=reward_row.attendanceRewardId
    )
    repository.save_attendance_log(db, new_log)

    # TODO: 유저 보상 지급 처리 (Users.money += rewardAmount)

    repository.commit_db(db)

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
