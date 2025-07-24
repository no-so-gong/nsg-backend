# app/core/database.py
import os
from databases import Database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 비동기용 엔진 생성
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True, future=True)

# SQLAlchemy 베이스 클래스
Base = declarative_base()

# databases 패키지용 비동기 DB 연결
database = Database(DATABASE_URL)

# 메타데이터 (테이블 스키마 관리용)
metadata = MetaData()

