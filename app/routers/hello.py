from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
def hello():
    print("프론트에서 요청 도착!")
    return {"message": "백엔드로부터 보낸 메시지입니다."}
