import os
import joblib
import pandas as pd
import math
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Optional

from app.api.care.schema import MLInput, PriceListResponse, CareActionResponse
from app.api.care.repository import (
    get_actions_by_category_and_evolution, get_category_by_name,
    get_action_by_id, calculate_recent_action_count, calculate_days_since_last_care,
    update_animal_emotion, log_action_result, update_user_pattern_bias,
    reset_animal_days_since_care, increment_all_animals_days_since_care
)
from app.api.pet.repository import get_animal_by_user_and_id
from app.models.category import Category
from app.api.user.service import process_transaction
from app.core.exception import CustomException

# .env 파일 로드
load_dotenv()

# 모델 경로 설정
model_path = os.getenv("MODEL_PATH", "./ML/emotion_model.pkl")

# 모델 불러오기
model = joblib.load(model_path)


def predict_and_apply_emotion_change(db: Session, user_id: UUID, animal_id: int, action_id: int) -> CareActionResponse:
    # 감정 변화 예측 및 적용
    
    # 1. 기본 데이터 조회
    animal = get_animal_by_user_and_id(db, user_id, animal_id)
    if not animal:
        raise CustomException(message="존재하지 않는 동물입니다.", status=404)
    
    action = get_action_by_id(db, action_id)
    if not action:
        raise CustomException(message="존재하지 않는 행동입니다.", status=404)
    
    # 2. 비즈니스 규칙 검사
    validate_action_requirements(animal, action, user_id)
    
    if animal.currentEmotion >= 100:
        raise CustomException(message="이미 감정이 최대치입니다.", status=400)
    
    # 3. 비용 확인 및 차감
    action_cost = action.price
    if action_cost > 0:
        try:
            process_transaction(db, user_id, -action_cost, "care", commit=False)
        except CustomException as e:
            raise e
    
    # 4. 행동 전 상태 정보 저장 (로그용)
    previous_emotion = float(animal.currentEmotion)
    previous_bias = float(animal.userPatternBias)
    days_since_care = calculate_days_since_last_care(db, animal_id, user_id)
    
    # 5. ML 모델 입력 구성
    ml_input = create_ml_input_from_db(db, animal, action, user_id)
    
    # 6. ML 모델 예측
    data = ml_input.dict()
    df_input = pd.DataFrame([data])
    predicted_delta = float(model.predict(df_input, validate_features=False)[0])
    
    # 7. 새로운 감정값 계산 (0-100 범위 제한)
    raw_new_emotion = previous_emotion + predicted_delta
    
    # 양수는 올림, 음수는 내림 처리
    if raw_new_emotion >= 0:
        new_emotion = math.ceil(raw_new_emotion)
    else:
        new_emotion = math.floor(raw_new_emotion)
    
    # 0-100 범위 제한
    new_emotion = max(0, min(100, new_emotion))
    
    # 8. 데이터베이스 업데이트 (트랜잭션으로 모든 변경사항 한번에 커밋)
    try:
        # 감정 상태 업데이트
        update_animal_emotion(db, animal_id, user_id, new_emotion)
        
        # 편애도 업데이트 (전이율 0.3 적용)
        update_user_pattern_bias(db, user_id, animal_id, transfer_rate=0.3)
        
        # 마지막 케어 이후 경과일 리셋 (action 수행 시 0으로)
        reset_animal_days_since_care(db, user_id, animal_id)
        
        # 행동 로그 기록 (행동 전 편애도와 경과 일수 포함)
        log_action_result(db, user_id, animal_id, action_id, previous_emotion, 
                         new_emotion, predicted_delta, previous_bias, days_since_care)
        
        db.commit()  # 모든 변경사항 (비용 차감, 감정 업데이트, 편애도 업데이트, 경과일 리셋, 로그 기록) 커밋
    except Exception as e:
        db.rollback()
        print(f"Database update error: {str(e)}")  # 디버깅용 로그
        raise CustomException(message=f"데이터베이스 업데이트 중 오류가 발생했습니다: {str(e)}", status=500)
    
    # 9. 응답 구성
    return CareActionResponse(
        predictedDelta=round(predicted_delta, 2),
        newEmotion=new_emotion,
        previousEmotion=previous_emotion,
        actionPerformed=action.name,
        message="감정 변화 예측 완료 및 반영됨",
        status=200
    )

def validate_action_requirements(animal, action, user_id: UUID) -> None:
    # 유효성 검사
    # 동물 소유권 확인
    if animal.userId != user_id:
        raise CustomException(message="해당 동물에 대한 권한이 없습니다.", status=403)
    
    # 가출 상태 확인
    if animal.isRunaway:
        raise CustomException(message="가출 중인 동물은 행동을 수행할 수 없습니다.", status=400)
    
    # 진화 단계 확인
    if animal.evolutionStage != action.evolutionStage:
        raise CustomException(message="현재 진화 단계와 맞지 않는 행동입니다.", status=400)

def create_ml_input_from_db(db: Session, animal, action, user_id: UUID) -> MLInput:
    # ML 입력 데이터 구성
    
    # 동물 타입 매핑 (animalId를 타입으로 변환)
    animal_type_mapping = {1: 'shiba', 2: 'duck', 3: 'chick'}
    animal_type = animal_type_mapping.get(animal.animalId, 'chick')
    
    # 액션명 매핑 (category와 level을 ML 모델 형식으로)
    category_obj = db.query(Category).filter(Category.categoryId == action.categoryId).first()
    category_name = category_obj.name if category_obj else 'feed'
    action_ml_name = f"{category_name}{action.actionLevel}"
    
    # 계산된 값들
    recent_action_count = calculate_recent_action_count(db, user_id, animal.animalId, action_ml_name)
    days_since_care = calculate_days_since_last_care(db, animal.animalId, user_id)
    
    # ML 모델 입력 구성
    ml_input_dict = {
        'current_emotion': int(float(animal.currentEmotion)),
        'action_count': recent_action_count,
        'user_pattern_bias': float(animal.userPatternBias),
        'days_since_last_care': days_since_care,
        
        # 동물 타입 OneHot 인코딩
        'animal_type_chick': 1 if animal_type == 'chick' else 0,
        'animal_type_duck': 1 if animal_type == 'duck' else 0,
        'animal_type_shiba': 1 if animal_type == 'shiba' else 0,
        
        # 액션 OneHot 인코딩 (선택된 액션만 1, 나머지는 0)
        'action_feed1': 1 if action_ml_name == 'feed1' else 0,
        'action_feed2': 1 if action_ml_name == 'feed2' else 0,
        'action_feed3': 1 if action_ml_name == 'feed3' else 0,
        'action_play1': 1 if action_ml_name == 'play1' else 0,
        'action_play2': 1 if action_ml_name == 'play2' else 0,
        'action_play3': 1 if action_ml_name == 'play3' else 0,
        'action_gift1': 1 if action_ml_name == 'gift1' else 0,
        'action_gift2': 1 if action_ml_name == 'gift2' else 0,
        'action_gift3': 1 if action_ml_name == 'gift3' else 0,
    }
    
    return MLInput(**ml_input_dict)

# 가격 정보 조회 서비스
def get_price_list_service(db: Session, category: str, animal_id: int, user_id: UUID) -> PriceListResponse:
    # 지원하는 카테고리 확인
    valid_categories = ['feed', 'play', 'gift']
    if category not in valid_categories:
        raise CustomException(
            message="올바르지 않은 카테고리입니다. (feed, play, gift 중 선택 가능)",
            status=400
        )
    
    # 동물 상태 정보 조회 (pet repository 직접 사용)
    animal = get_animal_by_user_and_id(db, user_id, animal_id)
    if not animal:
        raise CustomException(
            message="존재하지 않는 동물 ID입니다.",
            status=404
        )
    
    # 동물의 진화 단계 사용
    evolution_stage = animal.evolutionStage

    print(evolution_stage)
    
    # 해당 카테고리와 진화 단계의 액션들 조회
    actions = get_actions_by_category_and_evolution(db, category, evolution_stage)
    
    # 가격 딕셔너리 생성
    prices = {}
    for action in actions:
        prices[action.name] = action.price
    
    # 메시지 설정
    if evolution_stage == 1:
        message = f"카테고리 {category}의 가격 목록을 조회했습니다."
    else:
        message = "진화 단계가 높아서 가격이 올랐습니다."
    
    return PriceListResponse(
        animalId=animal_id,
        evolutionStage=evolution_stage,
        category=category,
        prices=prices,
        message=message,
        status=200
    )

def daily_increment_days_since_care_service(db: Session) -> dict:
    # 자정 배치용 - 모든 동물의 마지막 케어 이후 경과일 +1 증가
    try:
        increment_all_animals_days_since_care(db)
        return {
            "message": "모든 동물의 마지막 케어 이후 경과일이 1일씩 증가되었습니다.",
            "status": 200
        }
    except Exception as e:
        db.rollback()
        raise CustomException(message="경과일 업데이트 중 오류가 발생했습니다.", status=500)
