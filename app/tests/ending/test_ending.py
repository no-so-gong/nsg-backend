from uuid import uuid4
from datetime import date

from app.models.user import User
from app.models.animal import Animal
from app.models.moneyTransaction import MoneyTransaction
from app.models.attendance import AttendanceLog
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


