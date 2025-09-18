from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.exception import CustomException
from app.api.ending.repository import get_user_by_id
from app.models.minigameattempts import MinigameAttempt
from datetime import date
from app.api.minigame.repository import (
    get_minigame_by_id,
    get_user_by_id,
    get_user_daily_play_count,
    create_minigame_attempt,
    update_user_daily_play_count,
    get_today_play,
    create_today_play
)
from app.api.user.service import process_transaction
from app.api.minigame.schema import MinigameResultRequest, MinigameResultResponse, MinigameResultData
from app.core.exception import CustomException

# 미니게임 플레이 요청
def start_minigame(db: Session, user_id: UUID, game_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise CustomException("해당 유저를 찾을 수 없습니다.", 401)

    game = get_minigame_by_id(db, game_id)
    if not game:
        raise CustomException("해당 게임을 찾을 수 없습니다.", 404)

    max_play = game.maxPlay

    # 오늘 플레이 기록 조회
    play_record = get_today_play(db, user_id, game_id)
    if not play_record:
        play_record = create_today_play(db, user_id, game_id)

    # 횟수 제한 체크
    if play_record.playCount >= max_play:
        raise CustomException("오늘은 해당 게임을 더 이상 플레이할 수 없습니다.", 403)

    # 시작 가능 → playCount 증가 & MinigameAttempt 생성
    play_record.playCount += 1
    from datetime import datetime
    attempt = MinigameAttempt(userId=user_id, minigameId=game_id, startedAt=datetime.now())
    db.add(attempt)

    db.commit()
    db.refresh(play_record)

    remaining = max_play - play_record.playCount

    return {
        "message": "게임 시작 가능",
        "data": {"canPlay": True, "remainingPlays": remaining, "gameId": game_id},
        "status": 200
    }

def process_minigame_result(db: Session, user_id: UUID, game_id: int, result_data: MinigameResultRequest) -> MinigameResultResponse:
    # 미니게임 결과 처리
    try:
        # 1. 입력값 검증
        _validate_input(user_id, game_id, result_data)
        
        # 2. 게임 정보 조회
        minigame = get_minigame_by_id(db, game_id)
        if not minigame:
            raise CustomException(message="존재하지 않는 게임입니다", status=404)
        
        # 3. 사용자 정보 조회
        user = get_user_by_id(db, user_id)
        if not user:
            raise CustomException(message="사용자를 찾을 수 없습니다", status=404)
        
        # 4. 일일 플레이 횟수 확인
        today = date.today()
        current_play_count = get_user_daily_play_count(db, user_id, game_id, today)
        
        if current_play_count >= minigame.maxPlay:
            raise CustomException(message="일일 플레이 횟수를 초과했습니다", status=403)
        
        # 5. 데이터베이스 트랜잭션 처리
        try:
            # 미니게임 시도 기록 생성
            attempt_data = {
                'startedAt': result_data.startedAt,
                'completedAt': result_data.completedAt,
                'score': result_data.score,
                'timeSpent': result_data.timeSpent,
                'money': result_data.money,
                'gameId': game_id,
                'userId': user_id
            }
            create_minigame_attempt(db, attempt_data)
            
            # 일일 플레이 횟수 업데이트
            update_user_daily_play_count(db, user_id, game_id, today)
            
            # 재화 지급 (commit=False로 트랜잭션 관리)
            # money가 null이 아니고 0보다 클 때만 재화 지급
            if result_data.money is not None and result_data.money > 0:
                process_transaction(db, user_id, result_data.money, "minigame", commit=False)
            
            # 모든 작업이 성공하면 커밋
            db.commit()
            
            # 6. 성공 응답 반환
            response_data = MinigameResultData(
                startedAt=result_data.startedAt,
                completedAt=result_data.completedAt,
                score=result_data.score,
                timeSpent=result_data.timeSpent,
                money=result_data.money,
                gameId=game_id
            )
            
            # 게임 완료 여부에 따른 메시지 결정
            if result_data.completedAt is not None:
                message = "게임이 완료되고 보상이 지급되었습니다" if result_data.money and result_data.money > 0 else "게임이 완료되었습니다"
            else:
                message = "게임이 중단되었습니다"
            
            return MinigameResultResponse(
                status=200,
                message=message,
                data={"minigameResult": response_data}
            )
            
        except Exception as e:
            db.rollback()
            if isinstance(e, CustomException):
                raise e
            else:
                raise CustomException(message="미니게임 결과 처리 중 오류가 발생했습니다", status=500)
                
    except CustomException as e:
        raise e
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(message="데이터베이스 오류가 발생했습니다", status=500)
    except Exception as e:
        db.rollback()
        raise CustomException(message="서버 내부 오류가 발생했습니다", status=500)

def _validate_input(user_id: UUID, game_id: int, result_data: MinigameResultRequest):
    # 입력값 검증
    # gameId 범위 확인 (URL의 gameId 검증)
    if game_id not in [1, 2, 3]:
        raise CustomException(message="gameId는 1, 2, 3 중 하나여야 합니다", status=400)
    
    # 음수 값 확인 (null이 아닐 때만 검증)
    if result_data.score is not None and result_data.score < 0:
        raise CustomException(message="score는 0 이상이어야 합니다", status=400)
    if result_data.money is not None and result_data.money < 0:
        raise CustomException(message="money는 0 이상이어야 합니다", status=400)
    if result_data.timeSpent is not None and result_data.timeSpent < 0:
        raise CustomException(message="timeSpent는 0 이상이어야 합니다", status=400)
    
    # 시간 순서 확인 (둘 다 null이 아닐 때만 검증)
    if (result_data.completedAt is not None and result_data.startedAt is not None 
        and result_data.completedAt <= result_data.startedAt):
        raise CustomException(message="completedAt은 startedAt보다 이후 시각이어야 합니다", status=400)
