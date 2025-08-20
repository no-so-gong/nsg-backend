from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class BirthdayReward(Base):
    __tablename__ = 'birthdayRewards'

    rewardId = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    userId = Column(UUID(as_uuid=True), nullable=False)
    animalId = Column(Integer, nullable=False)

