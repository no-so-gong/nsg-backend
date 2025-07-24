from sqlalchemy import Column, Integer, String
from core.database import Base  # Base는 declarative_base()

class User(Base):
    __tablename__ = "users"

#    id = Column(Integer, primary_key=True, index=True)
#    username = Column(String(50), unique=True, nullable=False)
#   email = Column(String(100), unique=True, nullable=False)