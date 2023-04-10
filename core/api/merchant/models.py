from sqlalchemy import Column, String , Integer, DateTime, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import declarative_mixin
from core.utils.time import utc_time
from core.database.connection import Base
from datetime import date, time , datetime
from core.models.mixin import GenderType


class BusinessCategory(Base):

    __tablename__ = "business_category"
    id = Column(Integer, primary_key = True)
    category = Column(String(50), unique = True, nullable = False)



class MerchantProfile(Base): 

    __tablename__ = "merchant_profile"
    id = Column(Integer, primary_key=True)
    # users_id = Column(Integer, ForeignKey("users.id"), unique = True, nullable = False)
    sales_person_id = Column(String(10))
    merchant_account_number = Column(String(50), nullable=True)
    merchant_name = Column(String(50), nullable=True)
    authorized_person = Column(String(50), nullable=True)
    kyc_doc_type = Column(String(50), nullable=True)
    kyc_doc = Column(String(100), nullable=True)
    channel_partner_id = Column(Integer, nullable=True)
    dob = Column(Date, nullable=False)
    gender = Column(Enum(GenderType), nullable=False)
    profile_image = Column(String(1024), nullable=True)

class MerchantBusinessInfo(Base):

    __tablename__ = "merchant_business_info"
    id = Column(Integer, primary_key=True)
    merchant_id = Column(Integer, ForeignKey("merchant_profile.id"), unique = True, nullable = False)
    
    registered_business_number = Column(String(32),nullable = True)
    website = Column(String(100),nullable = True)
    business_description = Column(String(255),nullable = False)
    business_category = Column(Integer, ForeignKey("business_category.id"),nullable = False)
    dba = Column(String(255),nullable = True)
    address = Column(String(255), nullable=False)
    operating_address = Column(String(255), nullable=True)   
    postal_code = Column(String(20), nullable=False)
    operating_postal_code = Column(String(20), nullable=True)


class MerchantTaxInformation(Base):

    __tablename__ = "merchant_tax_information"
    id = Column(Integer, primary_key=True)
    merchant_id = Column(Integer, ForeignKey("merchant_profile.id"), nullable=False, unique=True)
    name_on_pan = Column(String(50), nullable=True)
    pan_number = Column(String(20), nullable=True)
    pan_doc = Column(String(1024), nullable=True)
    gstin_doc = Column(String(1024), nullable=True)
    tan_doc = Column(String(1024), nullable=True)
    id_proof = Column(String(100), nullable=True)
    # id_proof_type = Column(Integer, ForeignKey("id_proofs.id"), nullable=True)
    id_proof_doc = Column(String(1024), nullable=True)
    address_proof = Column(String(50), nullable=True)
    # address_proof_type = Column(Integer, ForeignKey("id_proofs.id"), nullable=True)
    address_proof_doc = Column(String(100), nullable=True)
