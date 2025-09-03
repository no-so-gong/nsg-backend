from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.animal import Animal
from app.models.emotionmessages import EmotionMessage
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
    # EmotionMessages 초기 데이터 주입
    seed_emotion_messages(db_session)

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



# 테스트 9: 감정 메시지 출력 테스트 - 긍정, 중립, 부정 케이스
def test_generate_emotion_message(client, db_session):
    # EmotionMessages 초기 데이터 주입 (없으면 삽입)
    seed_emotion_messages(db_session)

    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 테스트 케이스 정의: (predictedDelta, category, expected_level)
    test_cases = [
        (12, "play", 5),   
        (7, "feed", 4),    
        (2, "gift", 3),    
        (-3, "play", 3),  
        (-7, "feed", 2),   
        (-12, "gift", 1),  
    ]

    for predicted_delta, category, expected_level in test_cases:
        response = client.post(
            "/api/v1/cares/emotion-message",
            json={"predictedDelta": predicted_delta, "category": category}
        )
        assert response.status_code == 200
        data = response.json()

        # DB에서 해당 메시지 확인
        from app.api.care.repository import get_emotion_by_message
        expected_message_obj = get_emotion_by_message(db_session, category, expected_level)
        assert expected_message_obj is not None
        assert data["message"] == expected_message_obj.emotionMessage


        assert data["message"] == expected_message_obj.emotionMessage
        assert data["status"] == 200


# 헬퍼 함수: EmotionMessages 초기 데이터 주입
def seed_emotion_messages(db_session):
    from app.models.emotionmessages import EmotionMessage
    from app.models.category import Category

    if db_session.query(EmotionMessage).count() == 0:
        categories = {c.name: c.categoryId for c in db_session.query(Category).all()}
        initial_messages = [
            EmotionMessage(emotionMessage="신나게 뛰어놀아서 너무 좋아!", emotionMessageLevel=5, categoryId=categories["play"]),
            EmotionMessage(emotionMessage="너와 함께라 즐거워", emotionMessageLevel=4, categoryId=categories["play"]),
            EmotionMessage(emotionMessage="나랑 놀자 놀자!", emotionMessageLevel=3, categoryId=categories["play"]),
            EmotionMessage(emotionMessage="나랑 더 놀아주지...", emotionMessageLevel=2, categoryId=categories["play"]),
            EmotionMessage(emotionMessage="이제는 너랑 놀기 싫어", emotionMessageLevel=1, categoryId=categories["play"]),

            EmotionMessage(emotionMessage="맛있는 사료 다 먹었어!", emotionMessageLevel=5, categoryId=categories["feed"]),
            EmotionMessage(emotionMessage="잘 먹을게~", emotionMessageLevel=4, categoryId=categories["feed"]),
            EmotionMessage(emotionMessage="나...배불러^^.", emotionMessageLevel=3, categoryId=categories["feed"]),
            EmotionMessage(emotionMessage="다른 사료가 먹고싶은데...", emotionMessageLevel=2, categoryId=categories["feed"]),
            EmotionMessage(emotionMessage="이딴걸 먹으라고?", emotionMessageLevel=1, categoryId=categories["feed"]),

            EmotionMessage(emotionMessage="선물 고마워! 너무 좋아!!!", emotionMessageLevel=5, categoryId=categories["gift"]),
            EmotionMessage(emotionMessage="선물 고마워.", emotionMessageLevel=4, categoryId=categories["gift"]),
            EmotionMessage(emotionMessage="선물이네~", emotionMessageLevel=3, categoryId=categories["gift"]),
            EmotionMessage(emotionMessage="선물이 마음에 안 들어...", emotionMessageLevel=2, categoryId=categories["gift"]),
            EmotionMessage(emotionMessage="이게 뭐야...", emotionMessageLevel=1, categoryId=categories["gift"]),
        ]
        db_session.add_all(initial_messages)
        db_session.commit()
