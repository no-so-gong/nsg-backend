from sqlalchemy import Column, Integer, String, text
from app.core.database import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "Categories"

    categoryId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(10), nullable=True, server_default=text("'feed,play,gift'"))
    
    emotion_messages = relationship("EmotionMessage", back_populates="category")
