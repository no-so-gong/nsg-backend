from pydantic import BaseModel
from typing import List
from typing import Optional

# 보상 정보
class Reward(BaseModel):
    type: str
    amount: int

# 출석 로그 날짜별 board 정보
class BoardItem(BaseModel):
    day: int
    reward: int
    checkedIn: bool

# 출석 보상 조회 data 응답(/event/attendance) -> AttendanceResponse의 data 형식
class AttendanceResponseData(BaseModel):
    alreadyCheckedIn: bool
    totalAttendance: int
    todayIndex: int
    todayReward: Reward
    board: List[BoardItem]

# 출석 보상 조회 응답 틀(/event/attendance)
class AttendanceResponse(BaseModel):
    status: int
    message: str
    data: Optional[AttendanceResponseData]
