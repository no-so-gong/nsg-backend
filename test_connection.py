# test_connection.py
import asyncio
from app.core.database import database

async def test_db_connection():
    try:
        await database.connect()
        print("✅ PostgreSQL 연결 성공!")
        await database.disconnect()
    except Exception as e:
        print("❌ PostgreSQL 연결 실패:", e)

if __name__ == "__main__":
    asyncio.run(test_db_connection())
