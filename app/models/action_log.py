from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class ActionLog(Base):
    __tablename__ = "CareLogs"

    logId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("Users.userId"), nullable=False)
    animalId = Column(Integer, nullable=False)
    actionId = Column(Integer, ForeignKey("Actions.actionId"), nullable=False)
    emotionBefore = Column(Numeric(5, 2), nullable=False)
    emotionAfter = Column(Numeric(5, 2), nullable=False)
    predictedDelta = Column(Numeric(6, 2), nullable=False)
    actualDelta = Column(Numeric(6, 2), nullable=False)
    userPatternBias = Column(Numeric(5, 4), nullable=False)
    daysSinceLastCare = Column(Integer, nullable=False)
    performedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)