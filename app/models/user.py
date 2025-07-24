from sqlalchemy import Column, Integer, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    userId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    createdAt = Column(TIMESTAMP, nullable=False, server_default=func.now())
    money = Column(Integer, nullable=False, default=0)
