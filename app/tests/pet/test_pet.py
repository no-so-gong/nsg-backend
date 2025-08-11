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

# 동물 가출 처리 성공 테스트(/pets/{animalId}/runaway)
def test_runaway_pet_success(client):
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

    # 가출 처리 요청 (chick - animalId: 2)
    response = client.post(
        "/api/v1/pets/2/runaway",
        headers={"user-id": user_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "chick 동물이 성공적으로 가출 처리되었습니다." in data["message"]
    assert data["data"]["animalId"] == 2
    assert data["data"]["isRunaway"] == True

# 이미 가출 상태인 동물 가출 처리 시도 테스트
def test_runaway_pet_already_runaway(client):
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

    # 첫 번째 가출 처리 (성공)
    first_runaway = client.post(
        "/api/v1/pets/1/runaway",
        headers={"user-id": user_id}
    )
    assert first_runaway.status_code == 200

    # 두 번째 가출 처리 시도 (실패 - 이미 가출 상태)
    second_runaway = client.post(
        "/api/v1/pets/1/runaway",
        headers={"user-id": user_id}
    )
    
    assert second_runaway.status_code == 409
    data = second_runaway.json()
    assert data["status"] == 409
    assert "해당 동물은 이미 가출 상태입니다." in data["message"]

# 존재하지 않는 동물 ID로 가출 처리 시도 테스트
def test_runaway_pet_invalid_animal_id(client):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201

    # 생성된 유저 ID 사용
    user_id = user_response.json()["userId"]

    # 가출 처리 요청 (존재하지 않는 동물 ID)
    response = client.post(
        "/api/v1/pets/999/runaway",
        headers={"user-id": user_id}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == 400
    assert "유효하지 않은 동물 ID입니다." in data["message"]

# 사용자 ID 헤더가 없는 경우 테스트
def test_runaway_pet_missing_user_id(client):
    response = client.post("/api/v1/pets/1/runaway")
    
    assert response.status_code == 422  # Validation error for missing header

# 가출 처리 후 동물 상태 확인 테스트
def test_runaway_pet_status_check(client):
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

    # 가출 처리 전 상태 확인 (동물 정보 조회 API 사용)
    before_response = client.get(
        "/api/v1/pets/3",
        headers={"user-id": user_id}
    )
    assert before_response.status_code == 200
    before_data = before_response.json()
    assert before_data["isRunaway"] == False  # 가출 처리 전에는 False

    # 가출 처리
    runaway_response = client.post(
        "/api/v1/pets/3/runaway",
        headers={"user-id": user_id}
    )
    assert runaway_response.status_code == 200

    # 가출 처리 후 상태 확인 (GET /pets/{animalId}로 조회)
    after_response = client.get(
        "/api/v1/pets/3",
        headers={"user-id": user_id}
    )
    assert after_response.status_code == 200
    
    after_data = after_response.json()
    assert after_data["isRunaway"] == True  # 가출 처리 후에는 True
    assert after_data["animalId"] == 3
    