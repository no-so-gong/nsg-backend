# create_tables.py
from app.core.database import engine, Base, SessionLocal
import app.models  # 모델 등록 (user 등)
from app.models.attendance import AttendanceReward
from app.models.category import Category
from app.models.action import Action
from sqlalchemy import text

def create_tables():
    # 테이블 구조 변경사항만 적용 (기존 데이터는 유지)
    Base.metadata.create_all(bind=engine)
    print("테이블 구조 업데이트 완료")

# 개발용 - 초기 데이터 삽입 (필요시에만 별도로 실행)
def insert_initial_data():
    db = SessionLocal()
    try:
        # AttendanceRewards가 비어있을 때만 초기 데이터 삽입
        if db.query(AttendanceReward).count() == 0:
            initial_rewards = [
                AttendanceReward(rewardAmount=30, rewardType='money'),
                AttendanceReward(rewardAmount=40, rewardType='money'),
                AttendanceReward(rewardAmount=30, rewardType='money'),
                AttendanceReward(rewardAmount=40, rewardType='money'),
                AttendanceReward(rewardAmount=30, rewardType='money'),
                AttendanceReward(rewardAmount=40, rewardType='money'),
                AttendanceReward(rewardAmount=30, rewardType='money'),
            ]
            
            db.add_all(initial_rewards)
            db.commit()
            print("AttendanceRewards 초기 데이터 삽입 완료")
        else:
            print("AttendanceRewards 데이터가 이미 존재합니다.")
        
        # Categories가 비어있을 때만 초기 데이터 삽입
        if db.query(Category).count() == 0:
            initial_categories = [
                Category(name='play'),
                Category(name='feed'), 
                Category(name='gift'),
            ]
            
            db.add_all(initial_categories)
            db.commit()
            print("Categories 초기 데이터 삽입 완료")
        else:
            print("Categories 데이터가 이미 존재합니다.")

        # Actions가 비어있을 때만 초기 데이터 삽입 (예시 데이터)
        if db.query(Action).count() == 0:
            # 카테고리 ID를 가져와서 사용
            play_category = db.query(Category).filter(Category.name == 'play').first()
            feed_category = db.query(Category).filter(Category.name == 'feed').first()
            gift_category = db.query(Category).filter(Category.name == 'gift').first()
            
            initial_actions = [
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
            
            db.add_all(initial_actions)
            db.commit()
            print("Actions 초기 데이터 삽입 완료")
        else:
            print("Actions 데이터가 이미 존재합니다.")
        
    except Exception as e:
        db.rollback()
        print(f"초기 데이터 삽입 실패: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    insert_initial_data()
