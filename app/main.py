from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import hello
from app.routers import predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hello.router)
app.include_router(predict.router)
