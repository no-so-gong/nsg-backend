import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Optional

from app.api.care.schema import MLInput, PriceListResponse
from app.api.care.repository import get_animal_by_id, get_actions_by_category_and_evolution, get_category_by_name
from app.api.pet.service import get_pet_info_service
from app.core.exception import CustomException

# .env 파일 로드
load_dotenv()

# 모델 경로 설정
model_path = os.getenv("MODEL_PATH", "./ML/emotion_model.pkl")

# 모델 불러오기
model = joblib.load(model_path)

# ML 모델로부터 감정 변화량을 받아오는 함수 
def predict_emotion(input_data: MLInput) -> float:
    # 16개의 모든 필드를 그대로 받아서 예측에 사용
    data = input_data.dict()

    # DataFrame으로 변환
    df_input = pd.DataFrame([data])

    # 컬럼 순서 맞추기 필요 없음 -> validate_features=False 옵션 추가!
    prediction = model.predict(df_input, validate_features=False)[0]

    return float(prediction)

# 가격 정보 조회 서비스
def get_price_list_service(db: Session, category: str, animal_id: int, user_id: UUID) -> PriceListResponse:
    # 지원하는 카테고리 확인
    valid_categories = ['feed', 'play', 'gift']
    if category not in valid_categories:
        raise CustomException(
            message="지원하지 않는 카테고리입니다. (feed, play, gift 중 하나여야 합니다)",
            status=400
        )
    
    # 동물 상태 정보 조회 (pet service 사용)
    pet_info = get_pet_info_service(db, user_id, animal_id)
    if not pet_info:
        raise CustomException(
            message="존재하지 않는 동물 ID입니다.",
            status=404
        )
    
    # pet service에서 계산된 진화 단계 사용
    evolution_stage = pet_info.evolutionStage

    print(evolution_stage)
    
    # 해당 카테고리와 진화 단계의 액션들 조회
    actions = get_actions_by_category_and_evolution(db, category, evolution_stage)
    
    # 가격 딕셔너리 생성
    prices = {}
    for action in actions:
        prices[action.name] = action.price
    
    # 메시지 설정
    if evolution_stage == 1:
        message = f"카테고리 {category}의 가격 정보 조회 완료"
    else:
        message = "진화 단계에 따라 가격이 조정되어 반환되었습니다."
    
    return PriceListResponse(
        animalId=animal_id,
        evolutionStage=evolution_stage,
        category=category,
        prices=prices,
        message=message,
        status=200
    )
