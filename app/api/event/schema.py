from pydantic import BaseModel
from typing import List
from typing import Optional
from datetime import date

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

# 생일 보상 및 조회 관련 스키마

class BirthdayRewardData(BaseModel):
    animal_id: int
    name: str
    rewarded: bool
    reward: Reward   

class BirthdayRewardResponse(BaseModel):
    status: int
    message: str
    data: Optional[BirthdayRewardData]

class BirthdayAnimalInfo(BaseModel):
    animalId: int
    name: str
    rewarded: bool

class BirthdayAnimalsResponse(BaseModel):
    status: int
    message: str
    data: List[BirthdayAnimalInfo]


