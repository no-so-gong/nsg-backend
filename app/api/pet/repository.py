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


