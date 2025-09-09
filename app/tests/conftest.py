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
from app.models.category import Category
from app.models.action import Action
from app.models.attendance import AttendanceReward

# Create tables and insert initial data before running tests
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    
    # Insert initial test data if not exists
    session = SessionLocal()
    try:
        # Categories 초기 데이터
        if session.query(Category).count() == 0:
            categories = [
                Category(name='play'),
                Category(name='feed'), 
                Category(name='gift'),
            ]
            session.add_all(categories)
            session.commit()
            
        # Actions 초기 데이터
        if session.query(Action).count() == 0:
            play_category = session.query(Category).filter(Category.name == 'play').first()
            feed_category = session.query(Category).filter(Category.name == 'feed').first()
            gift_category = session.query(Category).filter(Category.name == 'gift').first()
            
            actions = [
                # Play actions
                Action(name='산책 가기', price=30, actionLevel=1, evolutionStage=1, categoryId=play_category.categoryId),
                Action(name='공 놀이', price=40, actionLevel=2, evolutionStage=1, categoryId=play_category.categoryId),
                Action(name='애견 카페 가기', price=50, actionLevel=3, evolutionStage=1, categoryId=play_category.categoryId),
                Action(name='산책 가기', price=50, actionLevel=1, evolutionStage=2, categoryId=play_category.categoryId),
                Action(name='공 놀이', price=60, actionLevel=2, evolutionStage=2, categoryId=play_category.categoryId),
                Action(name='애견 카페 가기', price=70, actionLevel=3, evolutionStage=2, categoryId=play_category.categoryId),
                Action(name='산책 가기', price=80, actionLevel=1, evolutionStage=3, categoryId=play_category.categoryId),
                Action(name='공 놀이', price=90, actionLevel=2, evolutionStage=3, categoryId=play_category.categoryId),
                Action(name='애견 카페 가기', price=100, actionLevel=3, evolutionStage=3, categoryId=play_category.categoryId),
                
                # Feed actions
                Action(name='시장 사료', price=30, actionLevel=1, evolutionStage=1, categoryId=feed_category.categoryId),
                Action(name='마트 사료', price=40, actionLevel=2, evolutionStage=1, categoryId=feed_category.categoryId),
                Action(name='유기농 사료', price=50, actionLevel=3, evolutionStage=1, categoryId=feed_category.categoryId),
                Action(name='시장 사료', price=50, actionLevel=1, evolutionStage=2, categoryId=feed_category.categoryId),
                Action(name='마트 사료', price=60, actionLevel=2, evolutionStage=2, categoryId=feed_category.categoryId),
                Action(name='유기농 사료', price=70, actionLevel=3, evolutionStage=2, categoryId=feed_category.categoryId),
                Action(name='시장 사료', price=80, actionLevel=1, evolutionStage=3, categoryId=feed_category.categoryId),
                Action(name='마트 사료', price=90, actionLevel=2, evolutionStage=3, categoryId=feed_category.categoryId),
                Action(name='유기농 사료', price=100, actionLevel=3, evolutionStage=3, categoryId=feed_category.categoryId),
                
                # Gift actions
                Action(name='장난감 사주기', price=30, actionLevel=1, evolutionStage=1, categoryId=gift_category.categoryId),
                Action(name='예쁜 옷 사주기', price=40, actionLevel=2, evolutionStage=1, categoryId=gift_category.categoryId),
                Action(name='유모차 사주기', price=50, actionLevel=3, evolutionStage=1, categoryId=gift_category.categoryId),
                Action(name='장난감 사주기', price=50, actionLevel=1, evolutionStage=2, categoryId=gift_category.categoryId),
                Action(name='예쁜 옷 사주기', price=60, actionLevel=2, evolutionStage=2, categoryId=gift_category.categoryId),
                Action(name='유모차 사주기', price=70, actionLevel=3, evolutionStage=2, categoryId=gift_category.categoryId),
                Action(name='장난감 사주기', price=80, actionLevel=1, evolutionStage=3, categoryId=gift_category.categoryId),
                Action(name='예쁜 옷 사주기', price=90, actionLevel=2, evolutionStage=3, categoryId=gift_category.categoryId),
                Action(name='유모차 사주기', price=100, actionLevel=3, evolutionStage=3, categoryId=gift_category.categoryId),
            ]
            session.add_all(actions)
            session.commit()
            
    except Exception as e:
        session.rollback()
        print(f"초기 데이터 삽입 실패: {e}")
    finally:
        session.close()
    
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