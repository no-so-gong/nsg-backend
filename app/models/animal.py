from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Animal(Base):
    __tablename__ = "animals"

    animalId = Column(Integer, primary_key=True, index=True)  # 1: 시바견, 2: 오리, 3: 병아리
    name = Column(String(10), nullable=False)
    isRunaway = Column(Boolean, nullable=False, server_default=text("false"))
    evolutionStage = Column(Integer, nullable=False, server_default=text("1"))
    currentEmotion = Column(Numeric(5, 2), nullable=False, server_default=text("50.00"))
    birthday = Column(Date, nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"), nullable=False)
    userPatternBias = Column(Numeric(3, 2), nullable=False, server_default=text("0.33"))
    daySinceLastCare = Column(Integer, nullable=False, server_default=text("0"))
