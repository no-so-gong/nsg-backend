# tests/user/test_user.py

from fastapi.testclient import TestClient
from app.main import app
from app.models.animal import Animal
from app.models.user import User

client = TestClient(app)

# 동물 이름 지어주기 테스트(/pets/nickname)
def test_nickname_animals(client):

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201

    # 생성된 유저 ID 사용
    user_id = user_response.json()["userId"]

    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }

    response = client.post(
        "/api/v1/pets/nickname",
        json=payload,
        headers={"user-id": user_id}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "동물 이름이 성공적으로 저장되었습니다."
    assert isinstance(data["data"], dict) or isinstance(data["data"], list)
    assert data["status"] == 200

# 동물 상태 상세 조회 테스트(/pets/{animalId})
def test_get_animal_info(client):

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201

    # 생성된 유저 ID 사용
    user_id = user_response.json()["userId"]

    # 동물 이름 지어주기
    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }

    nickname_response = client.post(
        "/api/v1/pets/nickname",
        json=payload,
        headers={"user-id": user_id}
    )
    assert nickname_response.status_code == 200

    # 동물 상태 조회 (예: animalId=1)
    get_response = client.get(
        "/api/v1/pets/1",
        headers={"user-id": user_id}
    )

    # 응답 검증
    assert get_response.status_code == 200
    data = get_response.json()

    assert data["animalId"] == 1
    assert data["name"] == "시바"
    assert 0.0 <= data["userPatternBias"] <= 1.0
    assert data["evolutionStage"] in [1, 2, 3]
    assert isinstance(data["currentEmotion"], int)
    assert isinstance(data["isRunaway"], bool)
    assert data["status"] == 200

# 가출한 동물 데려오기 성공 테스트(/pets/{animalId}/return)
def test_reset_emotion_success(client, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 동물 이름 지어주기
    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }
    nickname_response = client.post(
        "/api/v1/pets/nickname",
        json=payload,
        headers={"user-id": user_id}
    )
    assert nickname_response.status_code == 200

    # 테스트 대상 동물 선택 (animalId=1) → 감정 0으로, 유저 돈 100으로 세팅, 가출 상태로 먼저 변경
    animal = db_session.query(Animal).filter(Animal.userId == user_id, Animal.animalId == 1).first()
    assert animal is not None
    animal.currentEmotion = 0
    animal.isRunaway = True
    user = db_session.query(User).filter(User.userId == user_id).first()
    user.money = 100  # 비용(100) 이상으로 충전
    db_session.commit()

    # 감정 초기화 호출
    response = client.post(
        "/api/v1/pets/1/return",
        headers={"user-id": user_id}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "감정이 성공적으로 초기화되었습니다."
    assert data["status"] == 200
    assert data["animal"]["animalId"] == 1
    assert data["animal"]["current_emotion"] == 20
    # DB에서 isRunaway가 False로 변경되었는지 확인
    db_session.refresh(animal)
    assert animal.isRunaway is False


# 감정이 0이 아닐 때 초기화 불가 테스트
def test_reset_emotion_requires_zero(client):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 동물 이름 지어주기 (기본 감정 50)
    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }
    nickname_response = client.post(
        "/api/v1/pets/nickname",
        json=payload,
        headers={"user-id": user_id}
    )
    assert nickname_response.status_code == 200

    # 감정 초기화 호출 (감정이 0이 아님)
    response = client.post(
        "/api/v1/pets/1/return",
        headers={"user-id": user_id}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert data["message"] == "감정 초기화는 행복도가 0일 때만 가능합니다."


# 잔액 부족 시 초기화 불가 테스트
def test_reset_emotion_insufficient_money(client, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 동물 이름 지어주기
    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }
    nickname_response = client.post(
        "/api/v1/pets/nickname",
        json=payload,
        headers={"user-id": user_id}
    )
    assert nickname_response.status_code == 200

    # 감정 0으로, 잔액 0으로 설정
    animal = db_session.query(Animal).filter(Animal.userId == user_id, Animal.animalId == 2).first()
    assert animal is not None
    animal.currentEmotion = 0
    user = db_session.query(User).filter(User.userId == user_id).first()
    user.money = 0
    db_session.commit()

    # 감정 초기화 호출
    response = client.post(
        "/api/v1/pets/2/return",
        headers={"user-id": user_id}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert data["message"] == "잔액이 부족하여 감정을 초기화할 수 없습니다."


# 감정 데이터가 유효하지 않을 때(파싱 불가) 테스트
def test_reset_emotion_invalid_emotion_data(client, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 동물 이름 지어주기
    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }
    nickname_response = client.post(
        "/api/v1/pets/nickname",
        json=payload,
        headers={"user-id": user_id}
    )
    assert nickname_response.status_code == 200

    # 세션의 autoflush를 끄고, 감정을 비정상 값으로 주입하여 DB 플러시 에러 없이 파싱 오류 유도
    db_session.autoflush = False
    try:
        animal = db_session.query(Animal).filter(Animal.userId == user_id, Animal.animalId == 1).first()
        assert animal is not None
        animal.currentEmotion = "invalid-number"  # float() 변환 시 TypeError 유도

        # 호출
        response = client.post(
            "/api/v1/pets/1/return",
            headers={"user-id": user_id}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["status"] == 400
        assert data["message"] == "동물 감정 데이터가 유효하지 않습니다."
    finally:
        db_session.autoflush = True
