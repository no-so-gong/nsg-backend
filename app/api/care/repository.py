from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from app.models.animal import Animal
from app.models.action import Action
from app.models.category import Category
from app.models.emotionmessages import EmotionMessage

def get_animal_by_id(db: Session, animal_id: int, user_id: UUID) -> Optional[Animal]:
    return db.query(Animal).filter(
        and_(Animal.animalId == animal_id, Animal.userId == user_id)
    ).first()

def get_actions_by_category_and_evolution(db: Session, category_name: str, evolution_stage: int) -> List[Action]:
    return db.query(Action).join(Category).filter(
        and_(Category.name == category_name, Action.evolutionStage == evolution_stage)
    ).all()

def get_category_by_name(db: Session, category_name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == category_name).first()

def get_emotion_by_message(db: Session, category_name: str, level: int) -> Optional[EmotionMessage]:
    category_obj = get_category_by_name(db, category_name)
    if not category_obj:
        return None
    return db.query(EmotionMessage).filter(
        EmotionMessage.categoryId == category_obj.categoryId,
        EmotionMessage.emotionMessageLevel == level
    ).first()