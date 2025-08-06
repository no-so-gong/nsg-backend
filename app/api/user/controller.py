from fastapi import APIRouter, Depends, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.user.schema import UserCreateResponse, UserPropertyResponse
from app.api.user.service import create_user, get_user_property_service
from app.core.exception import CustomException
from app.core.database import get_db
from uuid import UUID

router = APIRouter(prefix="/api/v1/users", tags=["User"])

# 사용자를 하나 생성하는 api
@router.post("/start", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)  # POST /api/v1/users/start 요청이 오면 실행됨.
def start_game(db: Session = Depends(get_db)):                                                  # 요청 시 DB 세션을 get_db() 함수로부터 주입받음 (의존성 주입).
    user = create_user(db)                                                                      # 서비스 레이어에서 실제 유저 생성 로직을 호출.
    return {"userId": user.userId}                                                              # 생성된 userId를 JSON으로 반환.

# 사용자의 보유 코인을 조회하는 api
@router.get("/property", response_model=UserPropertyResponse)
def get_user_property(db: Session = Depends(get_db), user_id: UUID = Header(..., alias="user-id")):
    try:
        user = get_user_property_service(db, user_id)
        if user is None:
            raise CustomException("사용자 정보를 찾을 수 없습니다.", status=404)

        return JSONResponse(
            status_code=200,
            content={
                "money": user.money,
                "message": "현재 보유 골드 조회 성공",
                "status": 200
            }
        )
    except CustomException as e:
        raise e

