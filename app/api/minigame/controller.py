# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Header, Path
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Annotated

from app.core.database import get_db
from app.api.minigame.schema import MinigameResultRequest, MinigameResultResponse
from app.api.minigame.service import process_minigame_result
from app.core.exception import CustomException

router = APIRouter(prefix="/api/v1/minigames", tags=["minigame"])

@router.post("/{gameId}/result", response_model=MinigameResultResponse)
async def submit_minigame_result(
    gameId: Annotated[int, Path(ge=1, le=3, description="게임 ID (1, 2, 3 중 하나)")],
    result_data: MinigameResultRequest,
    user_id: Annotated[str, Header(alias="user-id", description="사용자 UUID")],
    db: Session = Depends(get_db)
):
    # 미니게임 결과 제출 및 보상 처리
    # - gameId: URL의 게임 ID (1, 2, 3 중 하나) - 로그에 저장됨
    # - user-id: 헤더에 포함된 사용자 UUID
    # - result_data: 미니게임 결과 데이터 (gameId 없음)
    
    # user-id 헤더 검증
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise CustomException(message="유효하지 않은 사용자 ID 형식입니다", status=400)
    
    # 게임 ID 검증 (Path 검증과 중복이지만 추가 보안)
    if gameId not in [1, 2, 3]:
        raise CustomException(message="gameId는 1, 2, 3 중 하나여야 합니다", status=400)
    
    # 미니게임 결과 처리
    return process_minigame_result(db, user_uuid, gameId, result_data)