from sqlalchemy.orm import Session
from typing import List, Dict
from uuid import UUID
from datetime import date

from app.api.pet.schema import AnimalInfoResponse
from app.api.pet.repository import create_animal, get_animal_by_user_and_id, reset_emotion_and_deduct_money, update_animal_runaway_status
from app.core.exception import CustomException

# 동물 이름 새로 지어주면서 만들기(/pets/nickname)
def register_pet_nicknames(db: Session, user_id: UUID, animal_list: List[dict]) -> Dict[str, str]:
    if len(animal_list) != 3:
        raise CustomException(message = "동물 이름은 3개 모두 입력되어야 합니다.", status=400)

    species_map = {1: "shiba", 2: "chick", 3: "duck"}
    birthday_map = {
        1: date(2001, 1, 4),    # 시바견
        2: date(2003, 12, 22),  # 병아리
        3: date(2004, 4, 19),   # 오리
    }
    result = {}

    for item in animal_list:
        animal_id = item["animalId"]
        name = item["name"]

        if animal_id not in species_map:
            raise CustomException(message = f"animalId {animal_id}는 잘못된 값입니다.", status=400)

        create_animal(
            db=db,
            user_id=user_id,
            animal_id=animal_id,
            name=name,
            birthday=birthday_map[animal_id]
        )

        result[species_map[animal_id]] = name

    return result

# 동물 상태 상세 조회(/pets/{animalId})
def get_pet_info_service(db: Session, user_id: UUID, animal_id: int) -> AnimalInfoResponse | None:
    animal = get_animal_by_user_and_id(db, user_id, animal_id)
    if animal is None:
        return None

    emotion = animal.currentEmotion
    if emotion >= 90:
        evolutionStage = 3
    elif emotion >= 70:
        evolutionStage = 2
    else:
        evolutionStage = 1

    return AnimalInfoResponse(
        animalId=animal.animalId,
        name=animal.name,
        userPatternBias=animal.userPatternBias,
        evolutionStage=evolutionStage,
        currentEmotion=animal.currentEmotion,
        isRunaway=animal.isRunaway,
        status=200
    )

# 가출한 동물 데려오기(/pets/{animalId}/return)
# 임의로 cost 100으로 설정(추후 논의 후 수정 필요)
def handle_emotion_reset(db: Session, user_id: UUID, animal_id: int, cost: int = 100) -> Dict:
    animal, remaining_money = reset_emotion_and_deduct_money(db, user_id, animal_id, cost)

    return {
        "animal": {
            "animalId": animal.animalId,
            "name": animal.name,
            "current_emotion": int(float(animal.currentEmotion)),
        },
        "money": remaining_money,
    }

# 동물 가출 처리(/pets/{animalId}/runaway)
def handle_animal_runaway(db: Session, user_id: UUID, animal_id: int) -> Dict:
    animal = update_animal_runaway_status(db, user_id, animal_id)
    
    return {
        "animalId": animal.animalId,
        "isRunaway": animal.isRunaway
    }
