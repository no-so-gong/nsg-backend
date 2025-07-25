from pydantic import BaseModel
from uuid import UUID

# 유저 생성 응답 dto(/users/start)
class UserCreateResponse(BaseModel):   
    userId: UUID
