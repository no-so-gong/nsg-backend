# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, SessionLocal, Base
from sqlalchemy.orm import Session
from uuid import uuid4
import sqlalchemy
from app.core.database import get_db
from app.core.config import KST
# Import all models to ensure they are registered with Base
from app.models.birthday import BirthdayReward
from app.models.animal import Animal

# Create tables before running tests
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    # Optional: drop tables after all tests are done
    # Base.metadata.drop_all(bind=engine)

# 실제 DB를 쓰되, 트랜잭션을 롤백하기 위한 fixture
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)
    session.begin_nested()

    # 트랜잭션 이벤트 리스너 등록 → SAVEPOINT rollback 방지용
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.begin_nested()

    yield session  # 이 안에서 테스트가 실행됨

    session.close()
    transaction.rollback()  # 테스트 끝나면 변경사항을 되돌림
    connection.close()

# FastAPI의 get_db 의존성 오버라이드
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)

