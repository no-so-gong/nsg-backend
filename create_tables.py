# create_tables.py
from app.core.database import engine, Base
import app.models  # 모델 등록 (user 등)

def create_tables():
    # 기존 테이블 모두 삭제 후 새로 생성
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
