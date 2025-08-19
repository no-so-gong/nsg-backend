from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BirthdayReward(Base):
    __tablename__ = 'birthdayRewards'

    rewardId = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    userId = Column(UUID(as_uuid=True), nullable=False)
    animalId = Column(Integer, nullable=False)
    userId2 = Column(UUID(as_uuid=True), nullable=False)

class Animal(Base):
    __tablename__ = "animals"   # 소문자로 지정

    animalId = Column(Integer, primary_key=True)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"))
    name = Column(String)
    birthday = Column(Date)
