from sqlalchemy import (Column, Date, DateTime, Enum,
                        ForeignKey, Integer, String)

from core.database.connection import Base
from core.models.mixin import GenderType, TimeStamp


class AdminProfile(Base, TimeStamp):

    __tablename__ = "admin_profile"
    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    dob = Column(Date)
    gender = Column(Enum(GenderType), nullable=False)
    last_login = Column(DateTime)
    profile_image = Column(String(1024))

    class Config:
        orm_mode = True