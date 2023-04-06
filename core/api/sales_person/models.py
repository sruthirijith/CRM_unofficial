from sqlalchemy import Column, String , Integer, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import declarative_mixin
from core.utils.time import utc_time
from core.database.connection import Base
from datetime import date, time


class Users( Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)



    
class track_time(Base):

    __tablename__ = "tracking_time"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    users_id         = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    date             =Column( String)
    login_time       = Column(DateTime)
    logout_time       = Column(DateTime)
    active_period    = Column(String)
    active           =Column(String)
    
     

     




