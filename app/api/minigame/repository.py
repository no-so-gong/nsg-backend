# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from uuid import UUID
from typing import Optional

from app.models.minigames import Minigame
from app.models.minigameattempts import MinigameAttempt
from app.models.userminigameplays import UserMinigamePlay
from app.models.user import User

def get_minigame_by_id(db: Session, game_id: int) -> Optional[Minigame]:
    # 게임 ID로 미니게임 정보 조회
    try:
        return db.query(Minigame).filter(Minigame.minigameId == game_id).first()
    except SQLAlchemyError as e:
        raise e

def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    # 사용자 ID로 사용자 정보 조회
    try:
        return db.query(User).filter(User.userId == user_id).first()
    except SQLAlchemyError as e:
        raise e

def get_user_daily_play_count(db: Session, user_id: UUID, game_id: int, play_date: date = None) -> int:
    # 사용자의 특정 게임 일일 플레이 횟수 조회
    if play_date is None:
        play_date = date.today()
    
    try:
        result = db.query(UserMinigamePlay).filter(
            UserMinigamePlay.userId == user_id,
            UserMinigamePlay.minigameId == game_id,
            UserMinigamePlay.playDate == play_date
        ).first()
        
        return result.playCount if result else 0
    except SQLAlchemyError as e:
        raise e

def create_minigame_attempt(db: Session, attempt_data: dict) -> MinigameAttempt:
    # 미니게임 시도 기록 생성
    try:
        attempt = MinigameAttempt(
            startedAt=attempt_data['startedAt'],
            completionAt=attempt_data['completedAt'],
            score=attempt_data['score'],
            timeSpent=attempt_data['timeSpent'],
            money=attempt_data['money'],
            minigameId=attempt_data['gameId'],
            userId=attempt_data['userId']
        )
        db.add(attempt)
        db.flush()
        return attempt
    except SQLAlchemyError as e:
        raise e

def update_user_daily_play_count(db: Session, user_id: UUID, game_id: int, play_date: date = None) -> UserMinigamePlay:
    # 사용자의 일일 플레이 횟수 업데이트
    if play_date is None:
        play_date = date.today()
    
    try:
        # 기존 기록 조회
        existing_play = db.query(UserMinigamePlay).filter(
            UserMinigamePlay.userId == user_id,
            UserMinigamePlay.minigameId == game_id,
            UserMinigamePlay.playDate == play_date
        ).first()
        
        if existing_play:
            # 기존 기록이 있으면 플레이 횟수 증가
            existing_play.playCount += 1
            db.flush()
            return existing_play
        else:
            # 기존 기록이 없으면 새로 생성
            new_play = UserMinigamePlay(
                userId=user_id,
                minigameId=game_id,
                playDate=play_date,
                playCount=1
            )
            db.add(new_play)
            db.flush()
            return new_play
    except SQLAlchemyError as e:
        raise e