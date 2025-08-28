# create_tables.py
from app.core.database import engine, Base, SessionLocal
import app.models  # 모델 등록 (user 등)
from app.models.attendance import AttendanceReward
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
        
    except Exception as e:
        db.rollback()
        print(f"AttendanceRewards 초기 데이터 삽입 실패: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
