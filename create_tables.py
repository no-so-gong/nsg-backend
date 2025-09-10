# create_tables.py
from app.core.database import engine, Base, SessionLocal
import app.models  # 모델 등록 (user 등)
from app.models.attendance import AttendanceReward
from app.models.category import Category
from app.models.action import Action
from sqlalchemy import text
from app.models.emotionmessages import EmotionMessage
from app.models.minigames import Minigame
from app.models.userminigameplays import UserMinigamePlay 
from app.models.minigameattempts import MinigameAttempt

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
        
         # EmotionMessages 초기값...
        if db.query(EmotionMessage).count() == 0:
            initial_emotion_messages = [
                # play
                EmotionMessage(emotionMessage="신나게 뛰어놀아서 너무 좋아!", emotionMessageLevel=5, categoryId=1),
                EmotionMessage(emotionMessage="너와 함께라 즐거워", emotionMessageLevel=4, categoryId=1),
                EmotionMessage(emotionMessage="나랑 놀자 놀자!", emotionMessageLevel=3, categoryId=1),
                EmotionMessage(emotionMessage="나랑 더 놀아주지...", emotionMessageLevel=2, categoryId=1),
                EmotionMessage(emotionMessage="이제는 너랑 놀기 싫어", emotionMessageLevel=1, categoryId=1),
                # Feed            
                EmotionMessage(emotionMessage="맛있는 사료 다 먹었어!", emotionMessageLevel=5, categoryId=2),
                EmotionMessage(emotionMessage="잘 먹을게~", emotionMessageLevel=4, categoryId=2),
                EmotionMessage(emotionMessage="나...배불러^^.", emotionMessageLevel=3, categoryId=2),
                EmotionMessage(emotionMessage="다른 사료가 먹고싶은데...", emotionMessageLevel=2, categoryId=2),
                EmotionMessage(emotionMessage="이딴걸 먹으라고?", emotionMessageLevel=1, categoryId=2),
                # gift
                EmotionMessage(emotionMessage="선물 고마워! 너무 좋아!!!", emotionMessageLevel=5, categoryId=3),
                EmotionMessage(emotionMessage="선물 고마워.", emotionMessageLevel=4, categoryId=3),
                EmotionMessage(emotionMessage="선물이네~", emotionMessageLevel=3, categoryId=3),
                EmotionMessage(emotionMessage="선물이 마음에 안 들어...", emotionMessageLevel=2, categoryId=3),
                EmotionMessage(emotionMessage="이게 뭐야...", emotionMessageLevel=1, categoryId=3),
            ]
            db.add_all(initial_emotion_messages)
            db.commit()
            print("EmotionMessages 초기 데이터 삽입 완료")
        else:
            print("EmotionMessages 데이터가 이미 존재합니다.")
        
        # Minigames가 비어있을 때만 초기 데이터 삽입
        if db.query(Minigame).count() == 0:
            initial_minigames = [
                Minigame(minigameId=1, name='똥 피하기', description='하늘에서 떨어지는 똥을 피하는 게임', maxPlay=3),
                Minigame(minigameId=2, name='테트리스', description='블록을 쌓아 가로 한 줄을 모두 채워 지우는 게임', maxPlay=3),
                Minigame(minigameId=3, name='뱀 게임', description='벽이나 자기 자신에게 부딪히지 않고 먹이를 먹는 게임', maxPlay=3),
            ]
            db.add_all(initial_minigames)
            db.commit()
            print("Minigames 초기 데이터 삽입 완료")
        else:
            print("Minigames 데이터가 이미 존재합니다.")

    except Exception as e:
        db.rollback()
        print(f"초기 데이터 삽입 실패: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    insert_initial_data()
