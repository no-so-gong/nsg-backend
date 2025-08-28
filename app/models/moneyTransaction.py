from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.core.database import Base

class TransactionDirection(enum.Enum):
    IN = "in"
    OUT = "out"

class MoneyTransaction(Base):
    __tablename__ = "moneyTransactions"

    txId = Column(String(20), primary_key=True, nullable=False)
    source = Column(String(20), nullable=False)
    amount = Column(Integer, nullable=False)
    direction = Column(Enum(TransactionDirection), nullable=False)
    createdAt = Column(TIMESTAMP, nullable=False, server_default=func.now())
    currentMoney = Column(Integer, nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"), nullable=False)
