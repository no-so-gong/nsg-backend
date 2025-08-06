from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.event.service import get_attendance_data, check_in_attendance
from app.api.event.schema import AttendanceResponseData, AttendanceResponse
from uuid import UUID

router = APIRouter(prefix="/api/v1/event", tags=["event"])

@router.get("/attendance", response_model=AttendanceResponse)
def attendance_info(user_id: UUID = Header(..., alias="user-id"), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=401, detail="user-id 헤더가 누락되었거나 유효하지 않습니다.")

    try:
        data = get_attendance_data(user_id, db)
        return {
            "status": 200,
            "message": "출석 정보 조회 성공",
            "data": data
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")


@router.post("/attendance/checkin", response_model=AttendanceResponse)
def attendance_checkin(user_id: UUID  = Header(..., alias="user-id"), db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=401, detail="user-id 헤더가 누락되었거나 유효하지 않습니다.")
    
    try:
        data = check_in_attendance( user_id, db)
        return {
            "status": 200,
            "message": "출석이 완료되었습니다.",
            "data": data
        }
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")
