from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Animal(Base):
    __tablename__ = "animals"

    animalId = Column(Integer, primary_key=True, index=True)
