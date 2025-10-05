from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.exception import CustomException
from app.api.ending.service import reset_game_service, get_ending_summary_service

router = APIRouter(prefix="/api/v1/endings", tags=["Ending"])


@router.post("/reset")
def reset_game(user_id: UUID = Header(..., alias="user-id"), db: Session = Depends(get_db)):
    try:
        data = reset_game_service(db, user_id)
        return JSONResponse(
            status_code=200,
            content={
                "message": "게임 설정이 초기화되었습니다. 이름 짓는 화면으로 이동합니다.",
                **data,
                "status": 200,
            },
        )
    except CustomException as e:
        return JSONResponse(status_code=e.status, content={"message": e.message, "status": e.status})
    except Exception:
        return JSONResponse(status_code=500, content={"message": "게임 초기화 중 오류가 발생했습니다.", "status": 500})


@router.get("/summary")
def get_ending_summary(user_id: UUID = Header(..., alias="user-id"), db: Session = Depends(get_db)):
    try:
        data = get_ending_summary_service(db, user_id)
        return JSONResponse(
            status_code=200,
            content={
                **data,
                "status": 200,
            },
        )
    except CustomException as e:
        return JSONResponse(status_code=e.status, content={"message": e.message, "status": e.status})
    except Exception:
        return JSONResponse(status_code=500, content={"message": "게임 요약 정보를 조회하는 중 오류가 발생했습니다.", "status": 500})
