from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, UniqueConstraint, Date, Enum, Time
from sqlalchemy.orm import relationship

from core.database.connection import Base
from core.models.mixin import TimeStamp, GenderType


class Users(TimeStamp, Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    referral_code = Column(String(10), nullable=False, unique=True)
    referred_by = Column(String(10))
    pin = Column(String(200))
    blocked = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    token = Column(String(200) ,unique=True)
    token_expired = Column(Boolean, default=False)
    user_role = relationship("UserRoles", back_populates="users", uselist=False)


class Roles(Base, TimeStamp):
    
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=False)
    description = Column(Text)


class UserRoles(Base, TimeStamp):

    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    users_id = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, primary_key=True)
    role = relationship("Roles")
    users = relationship("Users", back_populates="user_role", uselist=False)
    __table_args__ = (
        UniqueConstraint("users_id", "role_id", name="unique_user_role"),
    )


class SalesPersonProfile(Base, TimeStamp):

    __tablename__ = "sales_person_profile"
    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey("users.id"), unique=True)
    dob = Column(Date)
    gender = Column(Enum(GenderType), nullable=False)
    address1 = Column(String(100))
    address2 = Column(String(100))
    city = Column(String(20))
    district = Column(String(20))
    state = Column(String(20))
    country = Column(String(20))
    postal_code = Column(String(20))
    profile_image = Column(String(1024))
    designation = Column(String(30))

class MerchantStages(Base):

    __tablename__ = "merchant_stages"
    id = Column(Integer,primary_key=True)
    stage_name = Column(String(30))

class SalesPersonTimeTracking(Base):
    __tablename__ = "sales_person_time_tracking"
    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    log_in_time = Column(Time)
    log_out_time = Column(Time,nullable=True)
    active_login_time = Column(Time,nullable=True)
    active = Column(String(10))