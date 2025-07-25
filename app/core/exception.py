# app/core/exception.py
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 커스텀 예외 클래스
class CustomException(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message = message
        self.status = status

# 커스텀 예외 핸들러
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status,
        content={"message": exc.message, "status": exc.status}
    )

# FastAPI 기본 HTTPException을 커스터마이징
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "status": exc.status_code}
    )

# 입력 검증 에러 처리
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "입력값이 잘못되었습니다.", "status": 422}
    )
