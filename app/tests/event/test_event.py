from fastapi.testclient import TestClient

# 출석 체크 테스트(events/attendance/checkin)
def test_attendance_checkin(client: TestClient):
    # 먼저 유저 생성
    user_response = client.post("/api/v1/users/start")
    assert user_response.status_code == 201
    user_id = user_response.json()["userId"]

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