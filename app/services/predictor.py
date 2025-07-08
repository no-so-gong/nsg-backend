import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from app.schemas.input import EmotionInput

# .env 파일 로드
load_dotenv()

# 모델 경로 설정
model_path = os.getenv("MODEL_PATH", "./model/emotion_model.pkl")

# 모델 불러오기
model = joblib.load(model_path)

def predict_emotion(input_data: EmotionInput) -> float:
    # 16개의 모든 필드를 그대로 받아서 예측에 사용
    data = input_data.dict()

    # DataFrame으로 변환
    df_input = pd.DataFrame([data])

    # 컬럼 순서 맞추기 필요 없음 -> validate_features=False 옵션 추가!
    prediction = model.predict(df_input, validate_features=False)[0]

    return float(prediction)
