# create_tables.py
from app.core.database import engine, Base, SessionLocal
import app.models  # 모델 등록 (user 등)
from app.models.attendance import AttendanceReward

def create_tables():
    # 기존 테이블 모두 삭제 후 새로 생성
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # AttendanceRewards 테이블에 초기 데이터 삽입
    insert_initial_Data()

# 초기 데이터 삽입
def insert_initial_Data():
    db = SessionLocal()
    try:
        # 초기 AttendanceRewards 데이터
        initial_rewards = [
            AttendanceReward(attendanceRewardId=1, rewardAmount=30, rewardType='money'),
            AttendanceReward(attendanceRewardId=2, rewardAmount=40, rewardType='money'),
            AttendanceReward(attendanceRewardId=3, rewardAmount=30, rewardType='money'),
            AttendanceReward(attendanceRewardId=4, rewardAmount=40, rewardType='money'),
            AttendanceReward(attendanceRewardId=5, rewardAmount=30, rewardType='money'),
            AttendanceReward(attendanceRewardId=6, rewardAmount=40, rewardType='money'),
            AttendanceReward(attendanceRewardId=7, rewardAmount=30, rewardType='money'),
        ]
        
        db.add_all(initial_rewards)
        db.commit()
        print("AttendanceRewards 초기 데이터 삽입 완료")
        
    except Exception as e:
        db.rollback()
        print(f"AttendanceRewards 초기 데이터 삽입 실패: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
