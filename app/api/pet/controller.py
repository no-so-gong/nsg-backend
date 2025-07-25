# app/api/pet/controller.py
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.pet.schema import AnimalNicknameRequest, AnimalNicknameResponse
from app.api.pet.service import register_pet_nicknames
from app.core.exception import CustomException

router = APIRouter(prefix="/api/v1/pets", tags=["Pet"])

@router.post("/nickname", response_model=AnimalNicknameResponse)
def nickname_animals(request: AnimalNicknameRequest, db: Session = Depends(get_db)):
    try:
        result = register_pet_nicknames(db, request.userId, [a.dict() for a in request.animals]) # 이름 등록 처리
        return JSONResponse(
            status_code=200,
            content={
                "message": "동물 이름이 성공적으로 저장되었습니다.",
                "data": result,
                "status": 200
            }
        )
    except CustomException as e:
        raise e   # 커스텀 예외는 그대로 상위 예외 핸들러로 전달
