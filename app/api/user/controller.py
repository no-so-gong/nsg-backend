from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.user.schema import UserCreateResponse
from app.api.user.service import create_user
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/users", tags=["User"])

# 사용자를 하나 생성하는 api
@router.post("/start", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)  # POST /api/v1/users/start 요청이 오면 실행됨.
def start_game(db: Session = Depends(get_db)):                                                  # 요청 시 DB 세션을 get_db() 함수로부터 주입받음 (의존성 주입).
    user = create_user(db)                                                                      # 서비스 레이어에서 실제 유저 생성 로직을 호출.
    return {"userId": user.userId}                                                              # 생성된 userId를 JSON으로 반환.

# 유저 보유 돈 만드는 api

