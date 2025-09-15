from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from .service import start_minigame
from .schema import MinigameStartResponse
from uuid import UUID

router = APIRouter(prefix="/api/v1/minigames", tags=["Minigames"])


@router.post("/{game_id}/start", response_model=MinigameStartResponse, summary="미니게임 플레이 요청")
def start_game(
    game_id: int,
    user_id: UUID  = Header(..., alias="user-id"),
    db: Session = Depends(get_db)
):
    """
    특정 미니게임 플레이 시작 요청
    """
    return start_minigame(db=db, user_id=user_id, game_id=game_id)
