from sqlalchemy import Column, String, Integer
from app.core.database import Base
from enum import Enum

class CategoryEnum(str, Enum):
    feed = "feed"
    play = "play"
    gift = "gift"

# 특정 카테고리 가격 조회
class AnimalPrice(Base):
    __tablename__ = "animal_price"

    category = Column(String(20), primary_key=True)
    tier = Column(String(20), primary_key=True)
    base_price = Column(Integer, nullable=False)
    stage2_increment = Column(Integer, nullable=False)
    stage3_increment = Column(Integer, nullable=False)
