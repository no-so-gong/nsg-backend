import pytest
from uuid import uuid4
from datetime import datetime, date
from fastapi.testclient import TestClient

from app.models import User, Minigame, UserMinigamePlay, MinigameAttempt
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

def create_test_minigames_for_result_tests(db_session):
    if db_session.query(Minigame).count() == 0:
        minigames = [
            Minigame(minigameId=1, name="게임1", description="테스트 게임1", maxPlay=3),
            Minigame(minigameId=2, name="게임2", description="테스트 게임2", maxPlay=3),
            Minigame(minigameId=3, name="게임3", description="테스트 게임3", maxPlay=3)
        ]
        db_session.add_all(minigames)
        db_session.commit()


def test_start_minigame_success(db_session, test_user):
    create_test_minigames_for_result_tests(db_session)
    game = db_session.query(Minigame).filter(Minigame.minigameId == 1).first()

    repository.get_user_by_id = lambda db, uid: test_user

    result = start_minigame(db_session, user_id=test_user.userId, game_id=game.minigameId)
    assert result["status"] == 200


def test_start_minigame_exceed(db_session, test_user):
    create_test_minigames_for_result_tests(db_session)
    game = db_session.query(Minigame).filter(Minigame.minigameId == 1).first()

    # 유저 조회 mocking
    repository.get_user_by_id = lambda db, uid: test_user

    # 이미 오늘 플레이 기록 생성 (maxPlay=3이므로 3번 플레이한 것으로 설정)
    play = UserMinigamePlay(
        userId=test_user.userId,
        minigameId=game.minigameId,
        playDate=date.today(),
        playCount=3
    )
    db_session.add(play)
    db_session.commit()

    # 횟수 초과 시 CustomException 403 확인
    import pytest
    from app.core.exception import CustomException

    with pytest.raises(CustomException) as exc:
        start_minigame(db_session, user_id=test_user.userId, game_id=game.minigameId)

    assert exc.value.status == 403

def create_test_user_for_result_tests(db_session):
    user = User(userId=uuid4(), money=1000)
    db_session.add(user)
    db_session.commit()
    return str(user.userId)

def test_successful_game_completion(client, db_session):
    # 게임 정상 완료 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)
    test_game_id = 1

    # 정상 완료 요청 데이터
    request_data = {
        "score": 180,
        "money": 30,
        "timeSpent": 75,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:15Z"
    }

    # API 호출
    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == 200
    assert "보상이 지급되었습니다" in response_data["message"]
    assert response_data["data"]["minigameResult"]["score"] == 180
    assert response_data["data"]["minigameResult"]["money"] == 30
    assert response_data["data"]["minigameResult"]["gameId"] == test_game_id

    # 데이터베이스 상태 검증
    # 1. 미니게임 시도 기록 확인
    attempt = db_session.query(MinigameAttempt).filter(
        MinigameAttempt.userId == user_id,
        MinigameAttempt.minigameId == test_game_id
    ).first()
    assert attempt is not None
    assert attempt.score == 180
    assert attempt.money == 30

    # 2. 플레이 횟수 확인
    play_record = db_session.query(UserMinigamePlay).filter(
        UserMinigamePlay.userId == user_id,
        UserMinigamePlay.minigameId == test_game_id,
        UserMinigamePlay.playDate == date.today()
    ).first()
    assert play_record is not None
    assert play_record.playCount == 1

    # 3. 사용자 재화 확인
    user = db_session.query(User).filter(User.userId == user_id).first()
    assert user.money == 1030  # 초기 1000 + 보상 30

def test_interrupted_game_with_null_values(client, db_session):
    # 게임 중단 (null 값) 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)
    test_game_id = 1
    # 게임 중단 요청 데이터 (startedAt 제외 모든 값이 null)
    request_data = {
        "score": None,
        "money": None,
        "timeSpent": None,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": None
    }

    # API 호출
    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    # 디버깅용 응답 내용 출력
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == 200
    assert response_data["message"] == "게임이 중단되었습니다"
    assert response_data["data"]["minigameResult"]["score"] is None
    assert response_data["data"]["minigameResult"]["money"] is None
    assert response_data["data"]["minigameResult"]["gameId"] == test_game_id

    # 데이터베이스 상태 검증
    # 1. 미니게임 시도 기록 확인 (null 값들이 저장됨)
    attempt = db_session.query(MinigameAttempt).filter(
        MinigameAttempt.userId == user_id,
        MinigameAttempt.minigameId == test_game_id
    ).first()
    assert attempt is not None
    assert attempt.score is None
    assert attempt.money is None
    assert attempt.timeSpent is None
    assert attempt.completionAt is None

    # 2. 플레이 횟수는 증가함 (중단되어도 시도로 카운트)
    play_record = db_session.query(UserMinigamePlay).filter(
        UserMinigamePlay.userId == user_id,
        UserMinigamePlay.minigameId == test_game_id,
        UserMinigamePlay.playDate == date.today()
    ).first()
    assert play_record is not None
    assert play_record.playCount == 1

    # 3. 사용자 재화는 변화 없음 (보상 없음)
    user = db_session.query(User).filter(User.userId == user_id).first()
    assert user.money == 1000  # 초기값 그대로

def test_partial_null_values(client, db_session):
    # 일부 값만 null인 경우 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)
    test_game_id = 1

    # 일부 값만 null인 요청 데이터
    request_data = {
        "score": 100,
        "money": None,  # 보상 없음
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    # API 호출
    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "게임이 완료되었습니다"  # 보상 없음
    assert response_data["data"]["minigameResult"]["score"] == 100
    assert response_data["data"]["minigameResult"]["money"] is None

    # 사용자 재화는 변화 없음 (money가 null이므로 보상 없음)
    user = db_session.query(User).filter(User.userId == user_id).first()
    assert user.money == 1000

def test_daily_play_limit_exceeded(client, db_session):
    # 일일 플레이 횟수 초과 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)

    # 게임 ID 2 사용 (maxPlay = 3)
    game_id = 2

    # 첫 번째 플레이
    request_data = {
        "score": 100,
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    response1 = client.post(
        f"/api/v1/minigames/{game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response1.status_code == 200

    # 두 번째 플레이
    response2 = client.post(
        f"/api/v1/minigames/{game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response2.status_code == 200

    # 세 번째 플레이
    response3 = client.post(
        f"/api/v1/minigames/{game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response3.status_code == 200

    # 네 번째 플레이 (초과)
    response4 = client.post(
        f"/api/v1/minigames/{game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response4.status_code == 403
    response_data = response4.json()
    assert "일일 플레이 횟수를 초과했습니다" in response_data["message"]

def test_invalid_game_id(client, db_session):
    # 잘못된 게임 ID 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)

    request_data = {
        "score": 100,
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    # 잘못된 게임 ID (4)
    response = client.post(
        "/api/v1/minigames/4/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response.status_code == 422  # FastAPI Path validation error

def test_invalid_user_id(client, db_session):
    # 잘못된 사용자 ID 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    test_game_id = 1

    request_data = {
        "score": 100,
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    # 잘못된 UUID 형식
    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": "invalid-uuid"}
    )
    assert response.status_code == 400
    response_data = response.json()
    assert "유효하지 않은 사용자 ID 형식입니다" in response_data["message"]

def test_nonexistent_user(client, db_session):
    # 존재하지 않는 사용자 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    test_game_id = 1

    request_data = {
        "score": 100,
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    # 존재하지 않는 UUID
    fake_user_id = str(uuid4())
    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": fake_user_id}
    )
    assert response.status_code == 404
    response_data = response.json()
    assert "사용자를 찾을 수 없습니다" in response_data["message"]

def test_negative_values_validation(client, db_session):
    # 음수 값 검증 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)
    test_game_id = 1

    # 음수 값이 포함된 요청 데이터
    request_data = {
        "score": -10,  # 음수
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response.status_code == 422  # Pydantic validation error

def test_invalid_time_order(client, db_session):
    # 잘못된 시간 순서 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)
    test_game_id = 1

    # completedAt이 startedAt보다 이전인 요청 데이터
    request_data = {
        "score": 100,
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:56:00Z",
        "completedAt": "2025-09-09T19:55:00Z"  # 시작 시간보다 이전
    }

    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )
    assert response.status_code == 422  # Pydantic validation error

def test_missing_user_id_header(client, db_session):
    # user-id 헤더 누락 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    test_game_id = 1

    request_data = {
        "score": 100,
        "money": 10,
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    # user-id 헤더 없이 요청
    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data
    )
    assert response.status_code == 422  # FastAPI validation error

def test_zero_money_reward(client, db_session):
    # 보상이 0원인 경우 테스트
    # 초기 데이터 설정
    create_test_minigames_for_result_tests(db_session)
    user_id = create_test_user_for_result_tests(db_session)
    test_game_id = 1

    request_data = {
        "score": 100,
        "money": 0,  # 보상 0원
        "timeSpent": 60,
        "startedAt": "2025-09-09T19:55:00Z",
        "completedAt": "2025-09-09T19:56:00Z"
    }

    response = client.post(
        f"/api/v1/minigames/{test_game_id}/result",
        json=request_data,
        headers={"user-id": user_id}
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "게임이 완료되었습니다"  # 보상 없음 메시지

    # 사용자 재화는 변화 없음
    user = db_session.query(User).filter(User.userId == user_id).first()
    assert user.money == 1000