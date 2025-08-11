from sqlalchemy.orm import Session
from app.models.animal import Animal
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
    
    animal.isRunaway = True
    db.commit()
    db.refresh(animal)
    return animal


