from fastapi.testclient import TestClient
from app.main import app

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