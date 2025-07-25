from pydantic import BaseModel
from uuid import UUID

class UserCreateResponse(BaseModel):    # 응답의 데이터 형식
    userId: UUID
