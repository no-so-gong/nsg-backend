from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID

from app.models.minigames import Minigame
from app.models.userminigameplays import UserMinigamePlay

class MinigameRepository:
    def __init__(self, db: Session):
        self.db = db
    def get_game_by_id(self, game_id: int) -> Minigame | None:
        return self.db.query(Minigame).filter(Minigame.minigameId == game_id).first()

    # 오늘 플레이 기록 조회
    def get_today_play(self, user_id: UUID, game_id: int) -> UserMinigamePlay | None:
        return (
            self.db.query(UserMinigamePlay)
            .filter(
                UserMinigamePlay.userId == user_id,
                UserMinigamePlay.minigameId == game_id,
                UserMinigamePlay.playDate == date.today()
            )
            .first()
        )

    # 오늘 기록 생성
    def create_today_play(self, user_id: UUID, game_id: int) -> UserMinigamePlay:
        play = UserMinigamePlay(
            userId=user_id,
            minigameId=game_id,
            playDate=date.today(),
            playCount=0
        )
        self.db.add(play)
        self.db.flush()
        return play
