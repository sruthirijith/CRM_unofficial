from typing import Optional
from pydantic import BaseModel, EmailStr , Field


class registration(BaseModel):
    full_name      : Optional[str]
    email          : Optional[EmailStr]
    password       : Optional[str]
    phone_number   : Optional[str]
    role_id        : int

class UserCreate(registration):
    country_code: Optional[str] 

class Login(BaseModel):
    email     :  Optional[EmailStr]
    password  :  str

    

class enroll(BaseModel):
    
    merchant_id                :int
    registered_business_name   :str  
    registered_business_number :int
    website                    :str
    business_description       :str


    