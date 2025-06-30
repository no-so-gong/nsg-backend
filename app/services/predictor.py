import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from app.schemas.input import EmotionInput

# .env 파일 로드
load_dotenv()

# 환경 변수에서 모델 경로 읽기
model_path = os.getenv("MODEL_PATH", "./model/emotion_model.pkl")
model = joblib.load(model_path)

def predict_emotion(input_data: EmotionInput) -> float:
    df_input = pd.DataFrame([input_data.dict()])
    prediction = model.predict(df_input)[0]
    return round(prediction, 2)