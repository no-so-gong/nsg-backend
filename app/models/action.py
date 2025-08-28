from sqlalchemy import Column, Integer, String, ForeignKey, text, CheckConstraint
from app.core.database import Base

class Action(Base):
    __tablename__ = "Actions"

    actionId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    price = Column(Integer, nullable=False)
    actionLevel = Column(Integer, nullable=False, server_default=text("1"))
    evolutionStage = Column(Integer, nullable=False, server_default=text("1"))
    categoryId = Column(Integer, ForeignKey("Categories.categoryId"), nullable=False)
    
    __table_args__ = (
        CheckConstraint('"actionLevel" BETWEEN 1 AND 3', name='check_actionLevel_range'),
        CheckConstraint('"evolutionStage" BETWEEN 1 AND 3', name='check_evolutionStage_range'),
    )

