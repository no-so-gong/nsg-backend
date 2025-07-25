from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Animal(Base):
    __tablename__ = "animals"

    animalId = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False)
    isRunaway = Column(Boolean, nullable=False, default=False)
    evolutionStage = Column(Integer, nullable=False, default=1)
    currentEmotion = Column(Numeric(5, 2), nullable=False, default=50.00)
    birthday = Column(Date, nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"), nullable=False)
    userPatternBias = Column(Numeric(3, 2), nullable=False, default=0.00)  # 파생 속성
    daySinceLastCare = Column(Integer, nullable=False, default=0)
