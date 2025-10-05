from uuid import uuid4
from datetime import date, timedelta

from app.models.user import User
from app.models.animal import Animal
from app.models.moneyTransaction import MoneyTransaction, TransactionDirection
from app.models.attendance import AttendanceLog, AttendanceReward
from app.models.birthday import BirthdayReward


def test_reset_game_success(client, db_session):
    # 1) 사용자 생성
    res = client.post("/api/v1/users/start")
    assert res.status_code == 201
    user_id = res.json()["userId"]

    # 2) 동물 이름 등록 (Animals 생성)
    nickname_payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "병아리"},
            {"animalId": 3, "name": "오리"},
        ]
    }
    res_nick = client.post(
        "/api/v1/pets/nickname",
        json=nickname_payload,
        headers={"user-id": user_id},
    )
    assert res_nick.status_code == 200

    # 3) MoneyTransactions, AttendanceLog, BirthdayReward 생성
    # 3-1) 거래 하나 생성 (MoneyTransactions 생성)
    tx_payload = {"amount": 100, "source": "test"}
    res_tx = client.post(
        "/api/v1/users/transactions",
        json=tx_payload,
        headers={"user-id": user_id},
    )
    assert res_tx.status_code == 201

    # 3-2) 출석 로그/생일 보상 더미 데이터 삽입
    # AttendanceReward가 없을 수도 있으므로 하나 확보
    from app.models.attendance import AttendanceReward

    reward = db_session.query(AttendanceReward).first()
    if reward is None:
        reward = AttendanceReward(rewardAmount=10, rewardType="money")
        db_session.add(reward)
        db_session.commit()

    db_session.add(AttendanceLog(date=date.today(), userId=user_id, attendanceRewardId=reward.attendanceRewardId))
    db_session.add(BirthdayReward(date=date.today(), userId=user_id, animalId=1))
    db_session.commit()

    # 4) 리셋 호출
    res_reset = client.post(
        "/api/v1/endings/reset",
        headers={"user-id": user_id},
    )
    assert res_reset.status_code == 200
    body = res_reset.json()
    assert body["status"] == 200
    assert body["money"] == 0
    assert body["totalPlayDays"] == 0
    assert body["totalUsedMoney"] == 0
    assert isinstance(body.get("animals"), list) and len(body["animals"]) == 3
    for a in body["animals"]:
        assert a["name"] is None
        assert a["current_emotion"] == 50
        assert a["isRunaway"] is False

    # 5) DB 상태 검증: 유저 및 관련 데이터 삭제 확인
    assert db_session.query(User).filter(User.userId == user_id).first() is None
    assert db_session.query(Animal).filter(Animal.userId == user_id).count() == 0
    assert (
        db_session.query(MoneyTransaction)
        .filter(MoneyTransaction.userId == user_id)
        .count()
        == 0
    )
    assert db_session.query(AttendanceLog).filter(AttendanceLog.userId == user_id).count() == 0
    assert db_session.query(BirthdayReward).filter(BirthdayReward.userId == user_id).count() == 0


def test_reset_game_user_not_found(client):
    # 존재하지 않는 유저로 호출
    fake_id = str(uuid4())
    res = client.post(
        "/api/v1/endings/reset",
        headers={"user-id": fake_id},
    )
    # 서비스에서 404 CustomException을 던지고 컨트롤러가 그대로 반영
    assert res.status_code == 404 or res.json().get("status") == 404


def test_get_ending_summary_success(client, db_session):
    """엔딩 요약 조회 성공 테스트"""
    # 1) 사용자 생성
    res = client.post("/api/v1/users/start")
    assert res.status_code == 201
    user_id = res.json()["userId"]

    # 2) 동물 3마리 생성
    nickname_payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "병아리"},
            {"animalId": 3, "name": "오리"},
        ]
    }
    res_nick = client.post(
        "/api/v1/pets/nickname",
        json=nickname_payload,
        headers={"user-id": user_id},
    )
    assert res_nick.status_code == 200

    # 3) AttendanceReward 확보
    reward = db_session.query(AttendanceReward).first()
    if reward is None:
        reward = AttendanceReward(rewardAmount=10, rewardType="money")
        db_session.add(reward)
        db_session.commit()

    # 4) 출석 로그 추가 (연속 3일)
    today = date.today()
    for i in range(3):
        attendance_date = today - timedelta(days=i)
        db_session.add(AttendanceLog(
            date=attendance_date,
            userId=user_id,
            attendanceRewardId=reward.attendanceRewardId
        ))
    db_session.commit()

    # 5) MoneyTransaction 추가 (OUT 방향)
    db_session.add(MoneyTransaction(
        txId="test-tx-001",
        source="test",
        amount=100,
        direction=TransactionDirection.OUT,
        currentMoney=900,
        userId=user_id
    ))
    db_session.add(MoneyTransaction(
        txId="test-tx-002",
        source="test",
        amount=50,
        direction=TransactionDirection.OUT,
        currentMoney=850,
        userId=user_id
    ))
    db_session.commit()

    # 6) 동물 가출 횟수 증가
    animal1 = db_session.query(Animal).filter(
        Animal.userId == user_id,
        Animal.animalId == 1
    ).first()
    animal1.runawayCount = 2

    animal2 = db_session.query(Animal).filter(
        Animal.userId == user_id,
        Animal.animalId == 2
    ).first()
    animal2.runawayCount = 1
    db_session.commit()

    # 7) 모든 동물의 감정도를 100으로 설정
    for animal_id in [1, 2, 3]:
        animal = db_session.query(Animal).filter(
            Animal.userId == user_id,
            Animal.animalId == animal_id
        ).first()
        animal.currentEmotion = 100
    db_session.commit()

    # 8) 엔딩 요약 조회
    res = client.get(
        "/api/v1/endings/summary",
        headers={"user-id": user_id}
    )

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == 200
    assert body["totalPlayDays"] == 3  # 3일 출석
    assert body["totalUsedMoney"] == 150  # 100 + 50
    assert body["consecutiveAttendanceDays"] == 3  # 연속 3일
    assert body["runawayCount"] == 3  # 2 + 1
    assert "message" in body


def test_get_ending_summary_user_not_found(client):
    """존재하지 않는 유저로 엔딩 요약 조회"""
    fake_id = str(uuid4())
    res = client.get(
        "/api/v1/endings/summary",
        headers={"user-id": fake_id}
    )
    assert res.status_code == 404 or res.json().get("status") == 404


def test_get_ending_summary_game_not_finished(client, db_session):
    """게임이 끝나지 않은 상태에서 엔딩 요약 조회"""
    # 1) 사용자 생성
    res = client.post("/api/v1/users/start")
    assert res.status_code == 201
    user_id = res.json()["userId"]

    # 2) 동물 3마리 생성
    nickname_payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "병아리"},
            {"animalId": 3, "name": "오리"},
        ]
    }
    res_nick = client.post(
        "/api/v1/pets/nickname",
        json=nickname_payload,
        headers={"user-id": user_id},
    )
    assert res_nick.status_code == 200

    # 3) 동물 감정도를 100으로 설정하지 않음 (기본값 50)
    # 4) 엔딩 요약 조회 시도
    res = client.get(
        "/api/v1/endings/summary",
        headers={"user-id": user_id}
    )

    # 게임이 끝나지 않았으므로 400 에러
    assert res.status_code == 400 or res.json().get("status") == 400
    assert "게임이 종료되지 않았습니다" in res.json().get("message", "")


def test_get_ending_summary_consecutive_days_calculation(client, db_session):
    """연속 출석일 계산 로직 테스트"""
    # 1) 사용자 생성
    res = client.post("/api/v1/users/start")
    assert res.status_code == 201
    user_id = res.json()["userId"]

    # 2) 동물 3마리 생성 및 감정도 100 설정
    nickname_payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "병아리"},
            {"animalId": 3, "name": "오리"},
        ]
    }
    res_nick = client.post(
        "/api/v1/pets/nickname",
        json=nickname_payload,
        headers={"user-id": user_id},
    )
    assert res_nick.status_code == 200

    # 3) AttendanceReward 확보
    reward = db_session.query(AttendanceReward).first()
    if reward is None:
        reward = AttendanceReward(rewardAmount=10, rewardType="money")
        db_session.add(reward)
        db_session.commit()

    # 4) 출석 로그 추가 (연속 5일, 중간 1일 빠짐, 다시 2일 연속)
    # 최근: 오늘, 어제, 그제, 3일전, 4일전 (연속 5일)
    # 5일전은 빠짐
    # 6일전, 7일전 (이건 카운트 안됨)
    today = date.today()

    # 연속 5일
    for i in range(5):
        attendance_date = today - timedelta(days=i)
        db_session.add(AttendanceLog(
            date=attendance_date,
            userId=user_id,
            attendanceRewardId=reward.attendanceRewardId
        ))

    # 5일전은 빠짐

    # 6일전, 7일전 추가
    db_session.add(AttendanceLog(
        date=today - timedelta(days=6),
        userId=user_id,
        attendanceRewardId=reward.attendanceRewardId
    ))
    db_session.add(AttendanceLog(
        date=today - timedelta(days=7),
        userId=user_id,
        attendanceRewardId=reward.attendanceRewardId
    ))
    db_session.commit()

    # 5) 모든 동물의 감정도를 100으로 설정
    for animal_id in [1, 2, 3]:
        animal = db_session.query(Animal).filter(
            Animal.userId == user_id,
            Animal.animalId == animal_id
        ).first()
        animal.currentEmotion = 100
    db_session.commit()

    # 6) 엔딩 요약 조회
    res = client.get(
        "/api/v1/endings/summary",
        headers={"user-id": user_id}
    )

    assert res.status_code == 200
    body = res.json()
    # 연속 출석일은 가장 최근부터 5일
    assert body["consecutiveAttendanceDays"] == 5
    # 총 플레이 일수는 7일
    assert body["totalPlayDays"] == 7


def test_get_ending_summary_duplicate_attendance_dates(client, db_session):
    """중복 출석 날짜가 있을 때 정확히 계산되는지 테스트"""
    # 1) 사용자 생성
    res = client.post("/api/v1/users/start")
    assert res.status_code == 201
    user_id = res.json()["userId"]

    # 2) 동물 3마리 생성 및 감정도 100 설정
    nickname_payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "병아리"},
            {"animalId": 3, "name": "오리"},
        ]
    }
    res_nick = client.post(
        "/api/v1/pets/nickname",
        json=nickname_payload,
        headers={"user-id": user_id},
    )
    assert res_nick.status_code == 200

    # 3) AttendanceReward 확보
    reward = db_session.query(AttendanceReward).first()
    if reward is None:
        reward = AttendanceReward(rewardAmount=10, rewardType="money")
        db_session.add(reward)
        db_session.commit()

    # 4) 출석 로그 추가 (같은 날짜 중복)
    today = date.today()

    # 오늘 2번, 어제 2번, 그제 1번
    for _ in range(2):
        db_session.add(AttendanceLog(
            date=today,
            userId=user_id,
            attendanceRewardId=reward.attendanceRewardId
        ))

    for _ in range(2):
        db_session.add(AttendanceLog(
            date=today - timedelta(days=1),
            userId=user_id,
            attendanceRewardId=reward.attendanceRewardId
        ))

    db_session.add(AttendanceLog(
        date=today - timedelta(days=2),
        userId=user_id,
        attendanceRewardId=reward.attendanceRewardId
    ))
    db_session.commit()

    # 5) 모든 동물의 감정도를 100으로 설정
    for animal_id in [1, 2, 3]:
        animal = db_session.query(Animal).filter(
            Animal.userId == user_id,
            Animal.animalId == animal_id
        ).first()
        animal.currentEmotion = 100
    db_session.commit()

    # 6) 엔딩 요약 조회
    res = client.get(
        "/api/v1/endings/summary",
        headers={"user-id": user_id}
    )

    assert res.status_code == 200
    body = res.json()
    # 중복 제거 후 총 플레이 일수는 3일
    assert body["totalPlayDays"] == 3
    # 중복 제거 후 연속 출석일은 3일
    assert body["consecutiveAttendanceDays"] == 3

