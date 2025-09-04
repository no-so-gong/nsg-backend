from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.animal import Animal
from uuid import uuid4
from datetime import datetime, date
from app.core.config import KST
import random

# 테스트 1: 진화 단계 1 동물의 가격 목록 조회 성공 케이스
def test_get_price_list_evolution_stage_1_success(client, db_session):
    # 진화 단계 1 동물의 gift 카테고리 가격 목록 조회 테스트

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 진화 단계 1 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물1",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # API 호출 - gift 카테고리 가격 목록 조회
    response = client.get(
        f"/api/v1/cares/pricelist?category=gift&animalId={animal.animalId}",
        headers={"user-id": str(user_id)}
    )

    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["animalId"] == animal.animalId
    assert data["evolutionStage"] == 1
    assert data["category"] == "gift"
    assert "prices" in data
    assert data["status"] == 200

# 테스트 2: 진화 단계 2 동물의 가격 목록 조회 성공 케이스
def test_get_price_list_evolution_stage_2_success(client, db_session):
    # 진화 단계 2 동물의 feed 카테고리 가격 목록 조회 테스트 (가격 상승 확인)

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 진화 단계 2 동물 생성 (감정 70 이상으로 설정)
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물2",
        isRunaway=False,
        evolutionStage=2,
        currentEmotion=75.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # API 호출 - feed 카테고리 가격 목록 조회
    response = client.get(
        f"/api/v1/cares/pricelist?category=feed&animalId={animal.animalId}",
        headers={"user-id": str(user_id)}
    )

    # 응답 검증 - 진화 단계가 높으면 다른 메시지 반환
    assert response.status_code == 200
    data = response.json()
    assert data["animalId"] == animal.animalId
    assert data["evolutionStage"] == 2
    assert data["category"] == "feed"
    assert "prices" in data
    assert data["status"] == 200

# 테스트 3: 잘못된 카테고리 입력 시 에러 처리
def test_get_price_list_invalid_category(client, db_session):
    # 지원하지 않는 카테고리 입력 시 400 에러 반환 테스트

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # API 호출 - 잘못된 카테고리로 요청
    response = client.get(
        "/api/v1/cares/pricelist?category=invalid_category&animalId=1",
        headers={"user-id": str(user_id)}
    )

    # 에러 응답 검증
    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "올바르지 않은 카테고리입니다. (feed, play, gift 중 선택 가능)"
    assert data["status"] == 400

# 테스트 4: 존재하지 않는 동물 ID로 요청 시 에러 처리
def test_get_price_list_invalid_animal_id(client, db_session):
    # 존재하지 않는 동물 ID 입력 시 404 에러 반환 테스트

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # API 호출 - 존재하지 않는 동물 ID로 요청
    response = client.get(
        "/api/v1/cares/pricelist?category=gift&animalId=999",
        headers={"user-id": str(user_id)}
    )

    # 에러 응답 검증
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "존재하지 않는 동물 ID입니다."
    assert data["status"] == 404

# 테스트 5: feed 카테고리 가격 목록 조회 성공
def test_get_price_list_feed_category(client, db_session):
    # feed 카테고리 가격 목록 조회 성공 테스트

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 테스트 동물 생성
    animal_id = random.randint(1, 3) 
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # API 호출 - feed 카테고리 가격 목록 조회
    response = client.get(
        f"/api/v1/cares/pricelist?category=feed&animalId={animal.animalId}",
        headers={"user-id": str(user_id)}
    )

    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["animalId"] == animal.animalId
    assert data["evolutionStage"] == 1
    assert data["category"] == "feed"
    assert "prices" in data
    assert data["status"] == 200

# 테스트 6: play 카테고리 가격 목록 조회 성공
def test_get_price_list_play_category(client, db_session):
    # play 카테고리 가격 목록 조회 성공 테스트

    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 테스트 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # API 호출 - play 카테고리 가격 목록 조회
    response = client.get(
        f"/api/v1/cares/pricelist?category=play&animalId={animal.animalId}",
        headers={"user-id": str(user_id)}
    )

    # 응답 검증 (초기 데이터에 의존)
    assert response.status_code == 200
    data = response.json()
    assert data["animalId"] == animal.animalId
    assert data["evolutionStage"] == 1
    assert data["category"] == "play"
    assert "prices" in data
    assert data["status"] == 200

# 테스트 7: 필수 헤더(user-id) 누락 시 에러 처리
def test_get_price_list_missing_user_id_header(client, db_session):
    # 필수 헤더(user-id) 누락 시 422 에러 반환 테스트

    # API 호출 - user-id 헤더 없이 요청
    response = client.get("/api/v1/cares/pricelist?category=gift&animalId=1")

    # 에러 응답 검증
    assert response.status_code == 422

# 테스트 8: 필수 쿼리 파라미터 누락 시 에러 처리
def test_get_price_list_missing_query_parameters(client, db_session):
    # 필수 쿼리 파라미터 누락 시 422 에러 반환 테스트
    
    user_id = uuid4()
    
    # category 파라미터 누락 테스트
    response = client.get(
        "/api/v1/cares/pricelist?animalId=1",
        headers={"user-id": str(user_id)}
    )
    assert response.status_code == 422

    # animalId 파라미터 누락 테스트  
    response = client.get(
        "/api/v1/cares/pricelist?category=gift",
        headers={"user-id": str(user_id)}
    )
    assert response.status_code == 422

    # 모든 파라미터 누락 테스트
    response = client.get(
        "/api/v1/cares/pricelist",
        headers={"user-id": str(user_id)}
    )
    assert response.status_code == 422

# /action API 테스트 코드
# 테스트 9: 정상적인 케어 액션 수행 성공
def test_care_action_success(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 테스트용 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 유저 잔액 설정 (10000 골드)
    user = db_session.query(User).filter(User.userId == user_id).first()
    user.money = 10000
    db_session.commit()

    # Mock ML 모델 예측 결과
    def mock_predict(self, data, validate_features=False):
        return [15.5]  # 감정 증가량 예측 값
    
    # joblib.load를 mock하여 가짜 모델 반환
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 케어 액션 요청 (actionId=1은 feed1이라고 가정)
    action_request = {
        "animal_id": animal_id,
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert "predictedDelta" in data
    assert "newEmotion" in data
    assert "previousEmotion" in data
    assert "actionPerformed" in data
    assert data["message"] == "감정 변화 예측 완료 및 반영됨"
    assert data["status"] == 200
    assert data["previousEmotion"] == 50.0

# 테스트 10: 존재하지 않는 동물 ID로 케어 액션 수행 실패
def test_care_action_invalid_animal(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # Mock ML 모델
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 존재하지 않는 동물 ID로 요청
    action_request = {
        "animal_id": 999,
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 에러 응답 검증
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "존재하지 않는 동물입니다."
    assert data["status"] == 404

# 테스트 11: 존재하지 않는 액션 ID로 케어 액션 수행 실패
def test_care_action_invalid_action(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 테스트용 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # Mock ML 모델
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 존재하지 않는 액션 ID로 요청
    action_request = {
        "animal_id": animal_id,
        "action_id": 999
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 에러 응답 검증
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "존재하지 않는 행동입니다."
    assert data["status"] == 404

# 테스트 12: 다른 사용자 소유의 동물에 케어 액션 수행 실패
def test_care_action_unauthorized_animal(client, db_session, monkeypatch):
    # 첫 번째 유저 생성
    user_response1 = client.post("/api/v1/users/start")
    user1_id = user_response1.json()["userId"]
    
    # 두 번째 유저 생성
    user_response2 = client.post("/api/v1/users/start")
    user2_id = user_response2.json()["userId"]

    # 첫 번째 유저 소유의 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user1_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # Mock ML 모델
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 두 번째 유저가 첫 번째 유저의 동물에 액션 시도
    action_request = {
        "animal_id": animal_id,
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user2_id)}
    )

    # 권한 없음 에러 응답 검증
    assert response.status_code == 404  # animal not found for this user
    data = response.json()
    assert data["message"] == "존재하지 않는 동물입니다."
    assert data["status"] == 404

# 테스트 13: 가출 중인 동물에 케어 액션 수행 실패
def test_care_action_runaway_animal(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 가출 중인 테스트용 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=True,  # 가출 상태
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # Mock ML 모델
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 케어 액션 요청
    action_request = {
        "animal_id": animal_id,
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 에러 응답 검증
    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "가출 중인 동물은 행동을 수행할 수 없습니다."
    assert data["status"] == 400

# 테스트 14: 감정이 이미 최대치(100)인 동물에 케어 액션 수행 실패
def test_care_action_max_emotion(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 감정 최대치인 테스트용 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=100.0,  # 감정 최대치
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # Mock ML 모델
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 케어 액션 요청
    action_request = {
        "animal_id": animal_id,
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 에러 응답 검증
    assert response.status_code == 400
    data = response.json()
    assert data["message"] == "이미 감정이 최대치입니다."
    assert data["status"] == 400

# 테스트 15: 잔액 부족으로 케어 액션 수행 실패
def test_care_action_insufficient_funds(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 테스트용 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 유저 잔액을 매우 적게 설정
    user = db_session.query(User).filter(User.userId == user_id).first()
    user.money = 1  # 매우 적은 잔액
    db_session.commit()

    # Mock ML 모델
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [15.5]
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 케어 액션 요청
    action_request = {
        "animal_id": animal_id,
        "action_id": 1  # 이 액션이 1골드보다 비쌀 것으로 가정
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 잔액 부족 에러 응답 검증 (user service에서 발생)
    assert response.status_code == 400
    data = response.json()
    assert "잔액이 부족합니다" in data["message"]
    assert data["status"] == 400

# 테스트 16: 필수 헤더(user-id) 누락 시 에러 처리
def test_care_action_missing_user_id_header(client, db_session):
    # 케어 액션 요청 (user-id 헤더 없이)
    action_request = {
        "animal_id": 1,
        "action_id": 1
    }
    
    response = client.post("/api/v1/cares/action", json=action_request)

    # 에러 응답 검증
    assert response.status_code == 422

# 테스트 17: 잘못된 요청 본문으로 케어 액션 수행 실패
def test_care_action_invalid_request_body(client, db_session):
    user_response = client.post("/api/v1/users/start")
    user_id = user_response.json()["userId"]

    # animal_id 누락
    action_request = {
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )
    assert response.status_code == 422

    # action_id 누락
    action_request = {
        "animal_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )
    assert response.status_code == 422

    # 빈 요청 본문
    response = client.post(
        "/api/v1/cares/action",
        json={},
        headers={"user-id": str(user_id)}
    )
    assert response.status_code == 422

# 테스트 18: 감정값 경계 테스트 - 음수 감정값 처리
def test_care_action_negative_emotion_result(client, db_session, monkeypatch):
    # 먼저 유저 생성 API 호출
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_data = user_response.json()
    user_id = user_data["userId"]

    # 매우 낮은 감정의 테스트용 동물 생성
    animal_id = random.randint(1, 3)
    animal = Animal(
        animalId=animal_id,
        userId=user_id,
        name="테스트동물",
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=5.0,  # 낮은 감정
        birthday=date.today(),
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 유저 잔액 설정
    user = db_session.query(User).filter(User.userId == user_id).first()
    user.money = 10000
    db_session.commit()

    # Mock ML 모델이 매우 큰 음수값 반환
    def mock_load(path):
        class MockModel:
            def predict(self, data, validate_features=False):
                return [-20.0]  # 결과적으로 음수 감정이 될 것
        return MockModel()
    
    monkeypatch.setattr("joblib.load", mock_load)

    # 케어 액션 요청
    action_request = {
        "animal_id": animal_id,
        "action_id": 1
    }
    
    response = client.post(
        "/api/v1/cares/action",
        json=action_request,
        headers={"user-id": str(user_id)}
    )

    # 응답 검증 - 감정값이 0으로 제한되어야 함
    assert response.status_code == 200
    data = response.json()
    assert data["newEmotion"] >= 0  # 감정은 0 이상이어야 함
    assert data["previousEmotion"] == 5.0