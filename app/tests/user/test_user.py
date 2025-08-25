from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.moneyTransaction import MoneyTransaction, TransactionDirection
from uuid import uuid4
from datetime import datetime
from app.core.config import KST

# 사용자 생성 테스트(/users/start)
def test_start_user_creation(client):
    # API 요청
    response = client.post("/api/v1/users/start")

    # 응답 코드 검증
    assert response.status_code == 201

    # 응답 본문 파싱
    data = response.json()

    # 응답 필드 확인
    assert "userId" in data
    assert isinstance(data["userId"], str)

# 사용자 코인 조회 테스트(/users/property)
def test_user_property(client, db_session):
    user = User(
        userId=uuid4(),
        createdAt=datetime.now(KST),
        money=30
    )
    db_session.add(user)
    db_session.commit()

    response = client.get("/api/v1/users/property", headers={"user-id": str(user.userId)})
    assert response.status_code == 200

    data = response.json()
    assert data["money"] == 30
    assert data["message"] == "현재 보유 골드 조회 성공"
    assert data["status"] == 200

# 거래 성공 테스트(/users/transactions)
def test_transaction_success(client, db_session):
    # 테스트용 사용자 생성
    user = User(
        userId=uuid4(),
        createdAt=datetime.now(KST),
        money=1000
    )
    db_session.add(user)
    db_session.commit()

    # 입금 거래 요청
    transaction_data = {
        "amount": 500,
        "source": "test_source"
    }
    
    response = client.post(
        "/api/v1/users/transactions",
        json=transaction_data,
        headers={"user-id": str(user.userId)}
    )

    # 응답 코드 검증
    assert response.status_code == 201

    # 응답 본문 검증
    data = response.json()
    assert "txId" in data
    assert data["userId"] == str(user.userId)
    assert data["amount"] == 500
    assert data["source"] == "test_source"
    assert data["direction"] == "IN"
    assert data["currentMoney"] == 1500

# 사용자 없음 오류 테스트(/users/transactions)
def test_transaction_user_not_found(client, db_session):
    # 존재하지 않는 사용자 ID
    non_existent_user_id = uuid4()
    
    transaction_data = {
        "amount": 100,
        "source": "test_source"
    }
    
    response = client.post(
        "/api/v1/users/transactions",
        json=transaction_data,
        headers={"user-id": str(non_existent_user_id)}
    )

    # 응답 코드 검증 (404 Not Found)
    assert response.status_code == 404

    # 응답 본문 검증
    data = response.json()
    assert data["message"] == "사용자를 찾을 수 없습니다."
    assert data["status"] == 404

# 잔액 부족 오류 테스트(/users/transactions)
def test_transaction_insufficient_balance(client, db_session):
    # 잔액이 부족한 테스트용 사용자 생성
    user = User(
        userId=uuid4(),
        createdAt=datetime.now(KST),
        money=100
    )
    db_session.add(user)
    db_session.commit()

    # 잔액보다 많은 금액 출금 요청
    transaction_data = {
        "amount": -200,  # 음수로 출금 표현
        "source": "test_source"
    }
    
    response = client.post(
        "/api/v1/users/transactions",
        json=transaction_data,
        headers={"user-id": str(user.userId)}
    )

    # 응답 코드 검증 (400 Bad Request)
    assert response.status_code == 400

    # 응답 본문 검증
    data = response.json()
    assert "잔액이 부족합니다" in data["message"]
    assert data["status"] == 400

# 서버 오류 테스트(/users/transactions) - DB 오류 시뮬레이션
def test_transaction_server_error(client, db_session, monkeypatch):
    # 테스트용 사용자 생성
    user = User(
        userId=uuid4(),
        createdAt=datetime.now(KST),
        money=1000
    )
    db_session.add(user)
    db_session.commit()

    # SQLAlchemyError 발생을 시뮬레이션하는 함수
    def mock_commit():
        from sqlalchemy.exc import SQLAlchemyError
        raise SQLAlchemyError("Database connection error")

    # db.commit() 메소드를 mock으로 대체
    monkeypatch.setattr(db_session, "commit", mock_commit)
    
    transaction_data = {
        "amount": 100,
        "source": "test_source"
    }
    
    response = client.post(
        "/api/v1/users/transactions",
        json=transaction_data,
        headers={"user-id": str(user.userId)}
    )

    # 응답 코드 검증 (500 Internal Server Error)
    assert response.status_code == 500

    # 응답 본문 검증
    data = response.json()
    assert data["message"] == "데이터베이스 오류가 발생했습니다."
    assert data["status"] == 500