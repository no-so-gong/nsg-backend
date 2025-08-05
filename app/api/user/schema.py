from pydantic import BaseModel
from uuid import UUID

# 유저 생성 응답 dto(/users/start)
class UserCreateResponse(BaseModel):   
    userId: UUID

# 유저 코인 조회 응답 dto(/user/property)
class UserPropertyResponse(BaseModel):
    money: int
    message: str
    status: int