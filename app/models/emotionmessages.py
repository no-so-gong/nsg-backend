from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmotionMessage(Base):
    __tablename__ = "EmotionMessages"

    emotionMessageId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emotionMessageLevel = Column(Integer, nullable=False)
    emotionMessage = Column(String(255), nullable=False)
    categoryId = Column(Integer, ForeignKey("Categories.categoryId"), nullable=False)

    category = relationship("Category", back_populates="emotion_messages")