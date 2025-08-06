from datetime import date
from sqlalchemy.orm import Session
from app.models.attendance import AttendanceLog, AttendanceReward
from app.api.event.schema import AttendanceResponseData, Reward, BoardItem
from fastapi import HTTPException
from uuid import UUID

# 출석 보상 조회
def get_attendance_data(user_id: UUID, db: Session) -> AttendanceResponseData:
    today = date.today()

    logs = db.query(AttendanceLog).filter(AttendanceLog.userId == user_id).all()
    rewards = db.query(AttendanceReward).order_by(AttendanceReward.attendanceRewardId).all()

    total_attendance = len(logs)
    already_checked_in = any(log.date == today for log in logs)
    today_index = min(total_attendance + 1, 7)

    # 오늘 받을 보상
    today_reward_row = next((r for r in rewards if r.attendanceRewardId == today_index), None)
    today_reward = Reward(type=today_reward_row.rewardType, amount=today_reward_row.rewardAmount) if today_reward_row else Reward(type="money", amount=0)

    # board 생성
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

#  출석 보상 받기
def check_in_attendance(user_id: UUID, db: Session) -> AttendanceResponseData:
    today = date.today()

    # 오늘 출석 기록 있는지 체크
    existing = db.query(AttendanceLog).filter(AttendanceLog.userId == user_id, AttendanceLog.date == today).first()
    if existing:
        raise HTTPException(status_code=409, detail="이미 오늘 출석하셨습니다.")

    # 누적 출석 수 계산 (기존 로그 수)
    logs = db.query(AttendanceLog).filter(AttendanceLog.userId == user_id).all()
    total_attendance = len(logs) + 1  # 오늘 포함
    today_index = min(total_attendance, 7)

    # 오늘 출석 보상 정보 조회
    reward_row = db.query(AttendanceReward).filter(AttendanceReward.attendanceRewardId == today_index).first()
    if not reward_row:
        reward_row = AttendanceReward(attendanceRewardId=today_index, rewardAmount=0, rewardType="money")

    # 출석 로그 저장
    new_log = AttendanceLog(
        date=today,
        userId=user_id,
        attendanceRewardId=reward_row.attendanceRewardId
    )
    db.add(new_log)

    # TODO: 유저 보상 머니 지급 로직 추가 (Users 테이블 업데이트 등)
    # ex) user = db.query(User).filter(User.userId == user_id).first()
    # user.money += reward_row.rewardAmount

    db.commit()

    # 출석 기록 다시 조회 및 보상판(보드) 생성
    all_logs = logs + [new_log]
    checked_day_ids = {log.attendanceRewardId for log in all_logs}
    rewards = db.query(AttendanceReward).order_by(AttendanceReward.attendanceRewardId).all()

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