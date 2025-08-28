from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, ForeignKey, text, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Animal(Base):
    __tablename__ = "Animals"

    animalId = Column(Integer, primary_key=True, index=True)  # 1: 시바견, 2: 오리, 3: 병아리
    userId = Column(UUID(as_uuid=True), ForeignKey("Users.userId"), nullable=False)

    name = Column(String(10), nullable=False)
    isRunaway = Column(Boolean, nullable=False, server_default=text("false"))
    evolutionStage = Column(Integer, nullable=False, server_default=text("1"))
    currentEmotion = Column(Numeric(5, 2), nullable=False, server_default=text("50.00"))
    birthday = Column(Date, nullable=False)
    userPatternBias = Column(Numeric(3, 2), nullable=False, server_default=text("0.33"))
    daySinceLastCare = Column(Integer, nullable=False, server_default=text("0"))

    __table_args__ = ( # 복합 PK 설정
        PrimaryKeyConstraint('animalId', 'userId', name='pk_animal_user'),
    )
