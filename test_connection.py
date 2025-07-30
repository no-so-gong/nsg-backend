# test_connection.py

from app.core.database import SessionLocal
from sqlalchemy import text

def test_db_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ PostgreSQL 연결 성공!")
    except Exception as e:
        print("❌ PostgreSQL 연결 실패:", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_db_connection()
