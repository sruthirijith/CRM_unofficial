import enum

from sqlalchemy import Column, DateTime, Enum
from sqlalchemy.orm import declarative_mixin

from core.utils.time import utc_time


@declarative_mixin
class TimeStamp:
    created_at = Column(DateTime, default=utc_time(), nullable=False)
    updated_at = Column(DateTime, default=utc_time(), nullable=False)


class GenderType(enum.IntEnum):

    FEMALE = 1
    MALE = 2
    OTHER = 3
    NOTSPECIFIED = 4


class DeviceType(enum.IntEnum):

    ANDROID = 1
    IOS = 2
    NOTSPECIFIED = 3