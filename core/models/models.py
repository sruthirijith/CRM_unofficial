from sqlalchemy import Column, Integer, String, Text

from core.database.connection import Base
from core.models.mixin import TimeStamp

class Country(Base, TimeStamp):

    __tablename__ = "country"
    id = Column(Integer, primary_key = True)
    name = Column(String(60), nullable = False)
    flag = Column(String(1024),nullable = True)
    country_code = Column(String(16), nullable = False)
    currency_symbol = Column(Text, nullable = True)

class IDProofs(Base, TimeStamp):

    __tablename__ = "id_proofs"
    id = Column(Integer, primary_key = True)
    id_type = Column(String(30), nullable = False, unique = True)