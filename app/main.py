from fastapi import FastAPI
from app.routers import predict

app = FastAPI()

app.include_router(predict.router)