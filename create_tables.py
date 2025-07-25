# create_tables.py
import asyncio
from app.core.database import database
from app.core.database import engine, Base
import app.models  # 모델들 import

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # 모든 테이블 삭제
        await conn.run_sync(Base.metadata.create_all)  # 모든 테이블 생성
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(create_tables())
