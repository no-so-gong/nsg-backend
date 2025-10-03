from sqlalchemy.orm import Session
from app.models.animal import Animal
from app.models.user import User
from uuid import UUID
from datetime import date
from app.core.exception import CustomException

# 동물 이름 지어주면서 만들기(/pets/nickname)
def create_animal(db: Session, user_id: UUID, animal_id: int, name: str, birthday: date):
    existing = db.query(Animal).filter(Animal.animalId == animal_id, Animal.userId == user_id).first()
    if existing:
        raise CustomException(f"{animal_id}번 동물은 이미 존재합니다.", status=400)

    animal = Animal(
        animalId=animal_id,
        name=name,
        birthday=birthday,
        userId=user_id
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal

# 동물 상태 상세 조회(/pets/{animalId})
def get_animal_by_user_and_id(db: Session, user_id: UUID, animal_id: int):
    return db.query(Animal).filter(
        Animal.userId == user_id,
        Animal.animalId == animal_id
    ).first()

# 동물 가출 상태 업데이트(/pets/{animalId}/runaway)
def update_animal_runaway_status(db: Session, user_id: UUID, animal_id: int):
    animal = db.query(Animal).filter(
        Animal.userId == user_id,
        Animal.animalId == animal_id
    ).first()
    
    if animal is None:
        raise CustomException("유효하지 않은 동물 ID입니다.", status=400)
    
    if animal.isRunaway:
        raise CustomException("해당 동물은 이미 가출 상태입니다.", status=409)

    if animal.currentEmotion != 0:
        raise CustomException("현재 감정치가 0이 아니므로 가출 처리할 수 없습니다.", status=400)

    animal.isRunaway = True
    animal.runawayCount += 1
    db.commit()
    db.refresh(animal)
    return animal
  
# 가출한 동물 데려오기 처리(/pets/{animalId}/return)
def reset_emotion_and_deduct_money(db: Session, user_id: UUID, animal_id: int, cost: int):
    # 동물 조회 및 소유자 확인
    animal = db.query(Animal).filter(
        Animal.userId == user_id,
        Animal.animalId == animal_id
    ).first()

    if animal is None:
        raise CustomException("유효하지 않은 동물 ID입니다.", status=400)

    # 감정이 0일 때만 초기화 가능
    try:
        current_emotion_value = float(animal.currentEmotion)
    except (TypeError, ValueError):
        current_emotion_value = None

    if current_emotion_value is None:
        raise CustomException("동물 감정 데이터가 유효하지 않습니다.", status=400)

    if current_emotion_value != 0:
        raise CustomException("감정 초기화는 행복도가 0일 때만 가능합니다.", status=400)

    # 사용자 잔액 확인
    user = db.query(User).filter(User.userId == user_id).first()
    if user is None:
        raise CustomException("사용자 정보를 찾을 수 없습니다.", status=404)

    if user.money < cost:
        raise CustomException("잔액이 부족하여 감정을 초기화할 수 없습니다.", status=400)

    # 금액 차감 및 감정 초기화 + 가출 상태 복구
    user.money = int(user.money) - int(cost)
    animal.currentEmotion = 20
    animal.isRunaway = False

    db.commit()
    db.refresh(animal)
    db.refresh(user)

    return animal, int(user.money)

# 동물 진화 단계 업데이트
def update_animal_evolution_stage(db: Session, user_id: UUID, animal_id: int, evolution_stage: int):
    animal = db.query(Animal).filter(
        Animal.userId == user_id,
        Animal.animalId == animal_id
    ).first()
    
    if animal is None:
        raise CustomException("유효하지 않은 동물 ID입니다.", status=400)
    
    animal.evolutionStage = evolution_stage
    db.commit()
    db.refresh(animal)
    return animal
