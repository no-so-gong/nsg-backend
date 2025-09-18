from uuid import uuid4
from datetime import date

from app.models.minigames import Minigame
from app.models.userminigameplays import UserMinigamePlay
from app.models.minigameattempts import MinigameAttempt
from app.models.user import User
from app.core.exception import CustomException

def test_start_minigame_success(client, db_session):
    # 1) 유저 생성
    user_id = str(uuid4())
    user = User(userId=user_id)
    db_session.add(user)
    db_session.commit()

    # 2) 미니게임 생성
    game = Minigame(minigameId=1, name="테스트게임", maxPlay=3)
    db_session.add(game)
    db_session.commit()

    # 3) API 호출 (게임 시작)
    res = client.post(
        "/api/v1/minigames/1/start",
        headers={"user-id": user_id},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == 200
    assert body["data"]["canPlay"] is True
    assert body["data"]["remainingPlays"] == 2
    assert body["data"]["gameId"] == 1

    # 4) DB 검증: UserMinigamePlay, MinigameAttempt 생성 확인
    play_record = db_session.query(UserMinigamePlay).filter(
        UserMinigamePlay.userId == user_id,
        UserMinigamePlay.minigameId == 1,
        UserMinigamePlay.playDate == date.today()
    ).first()
    assert play_record is not None
    assert play_record.playCount == 1

    attempt = db_session.query(MinigameAttempt).filter(
        MinigameAttempt.userId == user_id,
        MinigameAttempt.minigameId == 1
    ).first()
    assert attempt is not None

def test_start_minigame_exceed(client, db_session):
    # 1) 유저 생성
    user_id = str(uuid4())
    user = User(userId=user_id)
    db_session.add(user)
    db_session.commit()

    # 2) 미니게임 생성 (maxPlay=1)
    game = Minigame(minigameId=2, name="테스트게임2", maxPlay=1)
    db_session.add(game)
    db_session.commit()

    # 3) 이미 오늘 플레이 기록 생성
    play_record = UserMinigamePlay(
        userId=user_id,
        minigameId=2,
        playDate=date.today(),
        playCount=1
    )
    db_session.add(play_record)
    db_session.commit()

    # 4) API 호출 → 횟수 초과
    res = client.post(
        "/api/v1/minigames/2/start",
        headers={"user-id": user_id},
    )
    assert res.status_code == 403
    body = res.json()
    assert body["status"] == 403
    assert body["data"]["canPlay"] is False
    assert body["data"]["remainingPlays"] == 0
