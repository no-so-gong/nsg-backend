from sqlalchemy import Column, Integer, String, Float
from core.database import Base

class Animal(Base):
    __tablename__ = "animals"
