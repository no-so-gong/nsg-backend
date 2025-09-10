from sqlalchemy import Column, Integer, String, TIMESTAMP, func, text

from app.core.database import Base

class Minigame(Base):
    __tablename__ = "Minigames"

    minigameId = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    description = Column(String(50))
    createdAt = Column(TIMESTAMP, nullable=False, server_default=func.now())
    maxPlay = Column(Integer, nullable=False, server_default=text("3"))