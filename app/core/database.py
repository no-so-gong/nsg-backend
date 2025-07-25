# app/core/database.py
import os
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 동기용 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

# 세션 생성기 (동기)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# SQLAlchemy 베이스 클래스
Base = declarative_base()

# 메타데이터 (테이블 스키마 관리용)
metadata = MetaData()

def get_db():
    db: Session = SessionLocal()    # DB 세션 하나 생성
    try:
        yield db                    # 세션을 외부에 "빌려줌"
    finally:
        db.close()                  # 사용이 끝나면 세션 닫음 (자원 해제)
