from fastapi.testclient import TestClient
from app.main import app
from app.models.animal import Animal
from app.models.animal_price import AnimalPrice

client = TestClient(app)

def setup_user_and_animals(db_session):
    user_resp = client.post("/api/v1/users/start")
    user_id = user_resp.json()["userId"]

    payload = {
        "animals": [
            {"animalId": 1, "name": "시바"},
            {"animalId": 2, "name": "꽥이"},
            {"animalId": 3, "name": "삐약이"}
        ]
    }
    client.post("/api/v1/pets/nickname", json=payload, headers={"user-id": user_id})
    return user_id

def setup_animal_price(db_session):
    db_session.query(AnimalPrice).delete()
    db_session.commit()

    db_session.add_all([
        # feed
        AnimalPrice(category="feed", tier="feed1", base_price=30, stage2_increment=20, stage3_increment=40),
        AnimalPrice(category="feed", tier="feed2", base_price=40, stage2_increment=20, stage3_increment=40),
        AnimalPrice(category="feed", tier="feed3", base_price=50, stage2_increment=20, stage3_increment=40),
        # play
        AnimalPrice(category="play", tier="play1", base_price=30, stage2_increment=20, stage3_increment=40),
        AnimalPrice(category="play", tier="play2", base_price=40, stage2_increment=20, stage3_increment=40),
        AnimalPrice(category="play", tier="play3", base_price=55, stage2_increment=20, stage3_increment=40),
        # gift
        AnimalPrice(category="gift", tier="gift1", base_price=30, stage2_increment=20, stage3_increment=40),
        AnimalPrice(category="gift", tier="gift2", base_price=40, stage2_increment=20, stage3_increment=40),
        AnimalPrice(category="gift", tier="gift3", base_price=50, stage2_increment=20, stage3_increment=40),
    ])
    db_session.commit()

# -------------------------
# 테스트 함수 예시
# -------------------------

def test_price_list_runaway_animal(client, db_session):
    user_id = setup_user_and_animals(db_session)
    setup_animal_price(db_session)

    animal = db_session.query(Animal).filter(
        Animal.userId == user_id, Animal.animalId == 2
    ).first()
    animal.isRunaway = True
    db_session.commit()

    resp = client.get(
        "/api/v1/pets/pricelist",
        headers={"user-id": user_id},
        params={"category": "play", "animalId": 2}
    )

    assert resp.status_code == 403
    data = resp.json()
    assert data["message"] == "동물이 가출한 상태입니다."
    assert data["status"] == 403

def test_price_list_invalid_category(client, db_session):
    user_id = setup_user_and_animals(db_session)
    setup_animal_price(db_session)

    resp = client.get(
        "/api/v1/pets/pricelist",
        headers={"user-id": user_id},
        params={"category": "invalid_category", "animalId": 1}
    )

    assert resp.status_code == 400
    data = resp.json()
    assert "지원하지 않는 카테고리입니다" in data["message"]

def test_price_list_invalid_animal_id(client, db_session):
    user_id = setup_user_and_animals(db_session)
    setup_animal_price(db_session)

    resp = client.get(
        "/api/v1/pets/pricelist",
        headers={"user-id": user_id},
        params={"category": "play", "animalId": 999}
    )

    assert resp.status_code == 404
    data = resp.json()
    assert "존재하지 않는 동물 ID입니다" in data["message"]
