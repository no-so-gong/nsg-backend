from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import threading
import time
import requests
from app.core.database import Base, engine

# 라우터
from app.api.care.controller import router as care_router
from app.api.user.controller import router as user_router

# 예외 핸들러
from app.core.exception import (
    CustomException,
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI()

# CORS 설정 (개발 중 전체 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예외 핸들러 등록
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 라우터 등록
app.include_router(care_router)
app.include_router(user_router)

# 서버가 실행되면 자동으로 "http://localhost:8000/api/v1/users/start"로 post를 보내서 유저 자동 생성
def call_start_api_after_server_ready():
    # 서버가 완전히 켜질 때까지 잠깐 기다림
    time.sleep(1.5)  # 상황에 따라 1~2초로 조절
    try:
        response = requests.post("http://localhost:8000/api/v1/users/start")
        print(f"✅ /start API 호출 성공: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"❌ /start API 호출 실패: {e}")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)                               # 테이블 자동 생성(python create_tables.py 와 동일)
    threading.Thread(target=call_start_api_after_server_ready).start()  # call_start_api_after_server_ready() 함수 호출을 통해 유저 생성