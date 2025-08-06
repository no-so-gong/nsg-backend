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