# app/api/pet/controller.py
from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.pet.schema import AnimalNicknameRequest, AnimalNicknameResponse, AnimalInfoResponse
from app.api.pet.service import register_pet_nicknames, get_pet_info_service
from app.core.exception import CustomException
from uuid import UUID

router = APIRouter(prefix="/api/v1/pets", tags=["Pet"])

# 동물 이름 지어주는 api
@router.post("/nickname", response_model=AnimalNicknameResponse)
def nickname_animals(request: AnimalNicknameRequest, db: Session = Depends(get_db), user_id: UUID = Header(..., alias="user-id")): # user_id UUID는 dto가 아닌 Header에서 user-id로 받음 
    try:
        result = register_pet_nicknames(db, user_id, [a.dict() for a in request.animals]) # 이름 등록 처리
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

# 동물 상태 상세 조회 api
@router.get("/{animalId}", response_model=AnimalInfoResponse)
def get_pet_info(animalId: int, db: Session = Depends(get_db) ,user_id: UUID = Header(..., alias="user-id")):
    pet_info = get_pet_info_service(db, user_id, animalId)
    if pet_info is None:
        raise CustomException(message = "해당 동물을 찾을 수 없습니다.", status=404)
    return pet_info    
