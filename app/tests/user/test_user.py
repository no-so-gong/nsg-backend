from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from uuid import uuid4
from datetime import datetime
from app.core.config import KST

# 사용자 생성 테스트
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