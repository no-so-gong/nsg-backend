from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import date
from app.api.event.service import get_attendance_data, check_in_attendance
from app.api.event.schema import AttendanceResponseData, AttendanceResponse
from uuid import UUID
from app.core.exception import CustomException
import traceback

from app.api.event.schema import BirthdayRewardResponse, BirthdayAnimalsResponse
from app.api.event.service import BirthdayService

router = APIRouter(prefix="/api/v1/event", tags=["event"])

@router.get("/attendance", response_model=AttendanceResponse)
def attendance_info(user_id: UUID = Header(..., alias="user-id"), db: Session = Depends(get_db)):
    if not user_id:
        raise CustomException(message = "user-id 헤더가 누락되었거나 유효하지 않습니다.", status=401)

    try:
        data = get_attendance_data(user_id, db)
        return {
            "status": 200,
            "message": "출석 정보 조회 성공",
            "data": data
        }
    except CustomException:
        raise
    except Exception:
        traceback.print_exc() 
        raise CustomException(message = "서버 내부 오류가 발생했습니다.", status=500)


@router.post("/attendance/checkin", response_model=AttendanceResponse)
def attendance_checkin(user_id: UUID  = Header(..., alias="user-id"), db: Session = Depends(get_db)):
    if not user_id:
        raise CustomException(message = "user-id 헤더가 누락되었거나 유효하지 않습니다.", status=401)

    try:
        data = check_in_attendance( user_id, db)
        return {
            "status": 200,
            "message": "출석이 완료되었습니다.",
            "data": data
        }
    except CustomException as e:
        raise e
    except Exception:
        raise CustomException(message = "서버 내부 오류가 발생했습니다.", status=500)

# 생일
@router.post("/birthday/reward", response_model=BirthdayRewardResponse)
def birthday_reward(
    user_id: UUID = Header(..., alias="user-id"),
    db: Session = Depends(get_db)
):
    if not user_id:
        raise CustomException(message="user-id 헤더가 누락되었거나 유효하지 않습니다.", status=401)

    service = BirthdayService(db)
    try:
        data = service.give_birthday_reward(user_id, date.today())
        return {
            "status": 200,
            "message": f"오늘은 {data['name']}의 생일입니다! 🎉 보상을 지급합니다.",
            "data": data
        }
    except CustomException as e:
        raise e
    except Exception:
        traceback.print_exc()
        raise CustomException(message="서버 내부 오류가 발생했습니다.", status=500)


@router.get("/birthday", response_model=BirthdayAnimalsResponse)
def birthday_animals(
    user_id: UUID = Header(..., alias="user-id"),
    db: Session = Depends(get_db)
):
    if not user_id:
        raise CustomException(message="user-id 헤더가 누락되었거나 유효하지 않습니다.", status=401)

    service = BirthdayService(db)
    try:
        animals = service.get_birthday_animals(user_id, date.today())
        if animals:
            return {
                "status": 200,
                "message": "오늘 생일인 동물이 있습니다.",
                "data": animals
            }
        else:
            return {
                "status": 200,
                "message": "오늘은 생일인 동물이 없습니다.",
                "data": []
            }
    except CustomException:
        raise
    except Exception:
        traceback.print_exc()
        raise CustomException(message="서버 내부 오류가 발생했습니다.", status=500)