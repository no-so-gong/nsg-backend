from sqlalchemy import Column, Integer, TIMESTAMP, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class MinigameAttempt(Base):
    __tablename__ = "MinigameAttempts"

    minigameAttemptId = Column(Integer, primary_key=True, index=True)
    startedAt = Column(TIMESTAMP, nullable=True)
    completionAt = Column(TIMESTAMP)
    score = Column(Integer)
    timeSpent = Column(Integer)
    money = Column(Integer)
    minigameId = Column(Integer, ForeignKey("Minigames.minigameId"), nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey("Users.userId"), nullable=False)