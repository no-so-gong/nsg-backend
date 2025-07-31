# tests/user/test_user.py

from fastapi.testclient import TestClient
from app.main import app

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