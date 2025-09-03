# -*- coding: utf-8 -*-

from fastapi.testclient import TestClient
from datetime import date
from app.models.animal import Animal
from app.models.birthday import BirthdayReward
from app.models.moneyTransaction import MoneyTransaction

# 출석 체크 테스트(events/attendance/checkin)
def test_attendance_checkin(client: TestClient, db_session):
    # 먼저 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 출석 체크 전 트랜잭션 개수 확인
    before_count = db_session.query(MoneyTransaction).filter_by(userId=user_id, source="attendance").count()

    # 출석 체크
    response = client.post(
        "/api/v1/events/attendance/checkin",
        headers={"user-id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "출석이 완료되었습니다."
    assert "data" in data
    assert data["status"] == 200
    assert "alreadyCheckedIn" in data["data"]
    assert "totalAttendance" in data["data"]
    assert "todayIndex" in data["data"]
    assert "todayReward" in data["data"]
    assert "board" in data["data"]
    
    # 새로운 머니 트랜잭션이 생성되었는지 확인
    after_count = db_session.query(MoneyTransaction).filter_by(userId=user_id, source="attendance").count()
    assert after_count == before_count + 1
    
    # 가장 최근 트랜잭션 확인
    latest_transaction = db_session.query(MoneyTransaction).filter_by(userId=user_id, source="attendance").order_by(MoneyTransaction.createdAt.desc()).first()
    assert latest_transaction is not None
    assert latest_transaction.amount > 0


# 출석 정보 조회 테스트(events/attendance)
def test_get_attendance_info(client: TestClient):
    # 먼저 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 출석 정보 조회
    response = client.get(
        "/api/v1/events/attendance",
        headers={"user-id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "출석 정보 조회 성공"
    assert "data" in data
    assert data["status"] == 200
    assert "alreadyCheckedIn" in data["data"]
    assert "totalAttendance" in data["data"]
    assert "todayIndex" in data["data"]
    assert "todayReward" in data["data"]
    assert "board" in data["data"]


# 생일 동물 조회 테스트 - 생일인 동물이 없는 경우(/events/birthday)
def test_get_birthday_animals_no_birthday(client: TestClient, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 생일이 아닌 동물 생성
    animal = Animal(
        animalId=1,
        userId=user_id,
        name="테스트 동물",
        birthday=date(2020, 1, 1),  # 오늘이 아닌 날짜
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 생일 동물 조회
    response = client.get(
        "/api/v1/events/birthday",
        headers={"user-id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "오늘은 생일인 동물이 없습니다."
    assert data["status"] == 200
    assert data["data"] == []


# 생일 동물 조회 테스트 - 생일인 동물이 있는 경우(/events/birthday)
def test_get_birthday_animals_with_birthday(client: TestClient, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 오늘 생일인 동물 생성
    today = date.today()
    animal = Animal(
        animalId=1,
        userId=user_id,
        name="생일 동물",
        birthday=today,
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 생일 동물 조회
    response = client.get(
        "/api/v1/events/birthday",
        headers={"user-id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "오늘 생일인 동물이 있습니다."
    assert data["status"] == 200
    assert len(data["data"]) == 1
    assert data["data"][0]["animalId"] == 1
    assert data["data"][0]["name"] == "생일 동물"
    assert data["data"][0]["rewarded"] == False


# 생일 보상 지급 테스트 - 성공 케이스(/events/birthday/reward)
def test_birthday_reward_success(client: TestClient, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 오늘 생일인 동물 생성
    today = date.today()
    animal = Animal(
        animalId=1,
        userId=user_id,
        name="생일 동물",
        birthday=today,
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 생일 보상 지급 전 트랜잭션 개수 확인
    before_count = db_session.query(MoneyTransaction).filter_by(userId=user_id, source="birthday").count()

    # 생일 보상 지급
    response = client.post(
        "/api/v1/events/birthday/reward",
        headers={"user-id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "오늘은 생일 동물의 생일입니다! 🎉 보상을 지급합니다." in data["message"]
    assert data["data"]["animal_id"] == 1
    assert data["data"]["name"] == "생일 동물"
    assert data["data"]["rewarded"] == True
    assert data["data"]["reward"]["type"] == "money"
    assert data["data"]["reward"]["amount"] == 100
    
    # 새로운 머니 트랜잭션이 생성되었는지 확인
    after_count = db_session.query(MoneyTransaction).filter_by(userId=user_id, source="birthday").count()
    assert after_count == before_count + 1
    
    # 가장 최근 트랜잭션 확인
    latest_transaction = db_session.query(MoneyTransaction).filter_by(userId=user_id, source="birthday").order_by(MoneyTransaction.createdAt.desc()).first()
    assert latest_transaction is not None
    assert latest_transaction.amount == 100


# 생일 보상 지급 테스트 - 생일이 아닌 경우(/events/birthday/reward)
def test_birthday_reward_not_birthday(client: TestClient, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 생일이 아닌 동물 생성
    animal = Animal(
        animalId=1,
        userId=user_id,
        name="테스트 동물",
        birthday=date(2020, 1, 1),  # 오늘이 아닌 날짜
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    db_session.commit()

    # 생일 보상 지급 시도
    response = client.post(
        "/api/v1/events/birthday/reward",
        headers={"user-id": user_id}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["message"] == "오늘 생일이 아님"


# 생일 보상 지급 테스트 - 이미 보상을 받은 경우(/events/birthday/reward)
def test_birthday_reward_already_rewarded(client: TestClient, db_session):
    # 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

    # 오늘 생일인 동물 생성
    today = date.today()
    animal = Animal(
        animalId=1,
        userId=user_id,
        name="생일 동물",
        birthday=today,
        isRunaway=False,
        evolutionStage=1,
        currentEmotion=50.0,
        userPatternBias=0.33,
        daySinceLastCare=0
    )
    db_session.add(animal)
    
    # 이미 보상 기록 생성
    reward = BirthdayReward(
        date=today,
        userId=user_id,
        animalId=1
    )
    db_session.add(reward)
    db_session.commit()

    # 생일 보상 지급 시도
    response = client.post(
        "/api/v1/events/birthday/reward",
        headers={"user-id": user_id}
    )
    assert response.status_code == 409
    data = response.json()
    assert data["message"] == "이미 선물 수령함"