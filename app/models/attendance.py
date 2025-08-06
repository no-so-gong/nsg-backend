from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class AttendanceReward(Base):
    __tablename__ = "AttendanceRewards"

    attendanceRewardId = Column(Integer, primary_key=True, index=True)
    rewardAmount = Column(Integer, nullable=False)
    rewardType = Column(String(20), default="money")


class AttendanceLog(Base):
    __tablename__ = "AttendanceLogs"

    attendanceId = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    userId = Column(UUID(as_uuid=True), nullable=False, index=True)
    attendanceRewardId = Column(Integer, ForeignKey("AttendanceRewards.attendanceRewardId"), nullable=False)
