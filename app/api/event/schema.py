from pydantic import BaseModel
from typing import List
from typing import Optional

class Reward(BaseModel):
    type: str
    amount: int

class BoardItem(BaseModel):
    day: int
    reward: int
    checkedIn: bool

class AttendanceResponseData(BaseModel):
    alreadyCheckedIn: bool
    totalAttendance: int
    todayIndex: int
    todayReward: Reward
    board: List[BoardItem]

class AttendanceResponse(BaseModel):
    status: int
    message: str
    data: Optional[AttendanceResponseData]


# 생일 보상 및 조회 관련 스키마
class BirthdayRewardInfo(BaseModel):
    type: str
    amount: int

class BirthdayRewardData(BaseModel):
    animal_id: int
    name: str
    rewarded: bool
    reward: BirthdayRewardInfo

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