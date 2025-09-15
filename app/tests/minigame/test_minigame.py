import pytest
from uuid import uuid4
from datetime import date

from app.models.user import User
from app.models.minigames import Minigame
from app.models.userminigameplays import UserMinigamePlay
from app.api.minigame.service import start_minigame
from app.core.exception import CustomException
from app.api.ending import repository

# db_session fixture는 pytest에서 제공하는 테스트용 세션

@pytest.fixture
def test_user(db_session):
    user_id = uuid4()
    user = User(userId=user_id)
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_game(db_session):
    game = Minigame(name="Test Game", maxPlay=3)
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)  # 자동 생성된 minigameId 가져오기
    return game

def test_start_minigame_success(db_session, test_user):
    game = Minigame(name="Test Game", maxPlay=3)
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)  # 자동 생성된 minigameId 사용

    repository.get_user_by_id = lambda db, uid: test_user

    result = start_minigame(db_session, user_id=test_user.userId, game_id=game.minigameId)
    assert result["status"] == 200


def test_start_minigame_exceed(db_session, test_user):
    # 게임 생성 (maxPlay=1)
    game = Minigame(name="Test Game Exceed", maxPlay=1)
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)

    # 유저 조회 mocking
    repository.get_user_by_id = lambda db, uid: test_user

    # 이미 오늘 플레이 기록 생성
    play = UserMinigamePlay(
        userId=test_user.userId,
        minigameId=game.minigameId,
        playDate=date.today(),
        playCount=1
    )
    db_session.add(play)
    db_session.commit()

    # 횟수 초과 시 CustomException 403 확인
    import pytest
    from app.core.exception import CustomException

    with pytest.raises(CustomException) as exc:
        start_minigame(db_session, user_id=test_user.userId, game_id=game.minigameId)

    assert exc.value.status == 403
