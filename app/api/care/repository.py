from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.models.animal import Animal
from app.models.action import Action
from app.models.category import Category
from app.models.action_log import ActionLog
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.emotionmessages import EmotionMessage

def get_actions_by_category_and_evolution(db: Session, category_name: str, evolution_stage: int) -> List[Action]:
    return db.query(Action).join(Category).filter(
        and_(Category.name == category_name, Action.evolutionStage == evolution_stage)
    ).all()

def get_category_by_name(db: Session, category_name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.name == category_name).first()

def get_action_by_id(db: Session, action_id: int) -> Optional[Action]:
    return db.query(Action).filter(Action.actionId == action_id).first()

def calculate_recent_action_count(db: Session, user_id: UUID, animal_id: int, action_ml_name: str) -> int:
    # 오늘(자정부터 현재까지) 해당 카테고리의 모든 액션 수행 횟수
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # action_ml_name에서 카테고리만 추출
        if action_ml_name.startswith('feed'):
            category = 'feed'
        elif action_ml_name.startswith('play'):
            category = 'play'
        elif action_ml_name.startswith('gift'):
            category = 'gift'
        else:
            return 0
        
        # 카테고리 ID 조회
        category_obj = db.query(Category).filter(Category.name == category).first()
        if not category_obj:
            return 0
        
        # 카테고리별로 모든 레벨의 액션 수 카운트 (actionLevel 조건 제거)
        count = db.query(func.count(ActionLog.logId)).join(Action).filter(
            and_(
                ActionLog.userId == user_id,
                ActionLog.animalId == animal_id,
                Action.categoryId == category_obj.categoryId,
                ActionLog.performedAt >= today_start
            )
        ).scalar()
        
        return count or 0
    except Exception as e:
        print(f"Error calculating recent action count: {str(e)}")
        return 0

def calculate_days_since_last_care(db: Session, animal_id: int, user_id: UUID) -> int:
    # 마지막 케어 이후 경과 일수
    try:
        last_care = db.query(func.max(ActionLog.performedAt)).filter(
            and_(
                ActionLog.animalId == animal_id,
                ActionLog.userId == user_id
            )
        ).scalar()
        
        if last_care and last_care is not None:
            return (datetime.now() - last_care).days
        return 0
    except Exception as e:
        print(f"Error calculating days since last care: {str(e)}")
        return 0

def update_animal_emotion(db: Session, animal_id: int, user_id: UUID, new_emotion: float) -> None:
    # 동물의 감정 상태 업데이트
    update_data = {"currentEmotion": new_emotion}
    
    # 감정이 0 이하가 되면 가출 상태로 변경
    if new_emotion <= 0:
        update_data["isRunaway"] = True
    
    db.query(Animal).filter(
        and_(Animal.animalId == animal_id, Animal.userId == user_id)
    ).update(update_data)

def get_all_user_animals(db: Session, user_id: UUID) -> List[Animal]:
    # 사용자의 모든 동물 조회
    return db.query(Animal).filter(Animal.userId == user_id).all()

def update_user_pattern_bias(db: Session, user_id: UUID, target_animal_id: int, transfer_rate: float = 0.3):
    # 편애도 업데이트 로직 (전이율 기반)
    animals = get_all_user_animals(db, user_id)
    
    if not animals:
        return
    
    # 현재 편애도 값들을 가져오기
    animal_biases = {}
    target_animal = None
    other_animals = []
    
    for animal in animals:
        current_bias = float(animal.userPatternBias)
        animal_biases[animal.animalId] = current_bias
        
        if animal.animalId == target_animal_id:
            target_animal = animal
        else:
            other_animals.append(animal)
    
    if not target_animal:
        return
    
    # 편애도 계산
    target_current_bias = animal_biases[target_animal_id]
    transfer_amount_per_animal = 0
    
    # 다른 동물들로부터 전이받을 양 계산
    for other_animal in other_animals:
        other_bias = animal_biases[other_animal.animalId]
        transfer_from_this = other_bias * transfer_rate
        transfer_amount_per_animal += transfer_from_this
    
    # 새로운 편애도 계산 (소수점 4자리로 반올림)
    new_target_bias = round(target_current_bias + transfer_amount_per_animal, 4)
    
    # 타겟 동물 업데이트
    db.query(Animal).filter(
        and_(Animal.userId == user_id, Animal.animalId == target_animal_id)
    ).update({"userPatternBias": new_target_bias})
    
    # 다른 동물들 업데이트 (각자 전이율만큼 감소, 소수점 4자리로 반올림)
    for other_animal in other_animals:
        current_bias = animal_biases[other_animal.animalId]
        new_bias = round(current_bias * (1 - transfer_rate), 4)
        
        db.query(Animal).filter(
            and_(Animal.userId == user_id, Animal.animalId == other_animal.animalId)
        ).update({"userPatternBias": new_bias})

def reset_animal_days_since_care(db: Session, user_id: UUID, animal_id: int) -> None:
    # 특정 동물의 마지막 케어 이후 경과일을 0으로 리셋
    db.query(Animal).filter(
        and_(Animal.userId == user_id, Animal.animalId == animal_id)
    ).update({"daySinceLastCare": 0})

def increment_all_animals_days_since_care(db: Session) -> None:
    # 모든 동물의 마지막 케어 이후 경과일을 1씩 증가 (자정 배치용)
    db.query(Animal).update(
        {"daySinceLastCare": Animal.daySinceLastCare + 1}
    )
    db.commit()

def log_action_result(db: Session, user_id: UUID, animal_id: int, action_id: int, 
                     emotion_before: float, emotion_after: float, predicted_delta: float,
                     user_pattern_bias: float, days_since_last_care: int) -> None:
    # 행동 결과를 로그에 기록
    actual_delta = emotion_after - emotion_before
    
    action_log = ActionLog(
        userId=user_id,
        animalId=animal_id,
        actionId=action_id,
        emotionBefore=emotion_before,
        emotionAfter=emotion_after,
        predictedDelta=predicted_delta,
        actualDelta=actual_delta,
        userPatternBias=user_pattern_bias,
        daysSinceLastCare=days_since_last_care
    )
    
    db.add(action_log)

def get_emotion_by_message(db: Session, category_name: str, level: int) -> Optional[EmotionMessage]:
    category_obj = get_category_by_name(db, category_name)
    if not category_obj:
        return None
    return db.query(EmotionMessage).filter(
        EmotionMessage.categoryId == category_obj.categoryId,
        EmotionMessage.emotionMessageLevel == level
    ).first()

