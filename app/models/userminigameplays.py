from sqlalchemy import Column, Integer, Date, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class UserMinigamePlay(Base):
    __tablename__ = "UserMinigamePlays"

    userMinigamePlayId = Column(Integer, primary_key=True, index=True)
    playDate = Column(Date, nullable=False, server_default=func.current_date())
    playCount = Column(Integer, nullable=False, server_default=text("0"))
    userId = Column(UUID(as_uuid=True), ForeignKey("Users.userId"), nullable=False)
    minigameId = Column(Integer, ForeignKey("Minigames.minigameId"), nullable=False)