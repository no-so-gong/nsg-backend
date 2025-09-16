from uuid import UUID
from sqlalchemy.orm import Session
from app.core.exception import CustomException
from app.api.ending.repository import get_user_by_id
from app.api.minigame.repository import MinigameRepository
from app.models.minigameattempts import MinigameAttempt

# 미니게임 플레이 요청
def start_minigame(db: Session, user_id: UUID, game_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise CustomException("해당 유저를 찾을 수 없습니다.", 401)

    repo = MinigameRepository(db)

    game = repo.get_game_by_id(game_id)
    if not game:
        raise CustomException("해당 게임을 찾을 수 없습니다.", 404)

    max_play = game.maxPlay

    # 오늘 플레이 기록 조회
    play_record = repo.get_today_play(user_id, game_id)
    if not play_record:
        play_record = repo.create_today_play(user_id, game_id)

    # 횟수 제한 체크
    if play_record.playCount >= max_play:
        raise CustomException("오늘은 해당 게임을 더 이상 플레이할 수 없습니다.", 403)

    # 시작 가능 → playCount 증가 & MinigameAttempt 생성
    play_record.playCount += 1
    attempt = MinigameAttempt(userId=user_id, minigameId=game_id)
    db.add(attempt)

    db.commit()
    db.refresh(play_record)

    remaining = max_play - play_record.playCount

    return {
        "message": "게임 시작 가능",
        "data": {"canPlay": True, "remainingPlays": remaining, "gameId": game_id},
        "status": 200
    }
