from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# 유저 생성 응답 dto(/users/start)
class UserCreateResponse(BaseModel):   
    userId: UUID

# 유저 코인 조회 응답 dto(/user/property)
class UserPropertyResponse(BaseModel):
    money: int
    message: str
    status: int

# 거래 요청 dto
class TransactionRequest(BaseModel):
    amount: int
    source: str

# 거래 성공 응답 dto
class TransactionResponse(BaseModel):
    txId: str
    userId: UUID
    amount: int
    source: str
    direction: str
    currentMoney: int
    createdAt: datetime

# 거래 실패 응답 dto
class TransactionErrorResponse(BaseModel):
    message: str
    status: int
    code: str = None