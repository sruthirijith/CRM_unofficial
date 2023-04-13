from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel

from core.models.mixin import GenderType
from core.api.admin.schema import UserCreate

class AdminCreate(UserCreate):
    password : str
    dob : date
    gender : GenderType

    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "full_name": "Test Test",
                "email" : "test@example.com",
                "phone_number" : "+919087654321",
                "country_code": "+91",
                "referred_by": "abcdef",
                "role_id": "2",
                "password" : "Test@1234",
                "dob" : "2022-01-30",
                "gender" : 1,
            },
        }

class UpdateAdminProfile(BaseModel):
    full_name : Optional[str]
    users_id : int
    dob : Optional[date]
    gender : Optional[GenderType]


    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "full_name": "Test Test",
                "users_id" : 1,
                "dob" : "2022-01-30",
                "gender" : 1,
            },
        }
        
class UserId(BaseModel):
    users_id : int

    class Config :
        orm_mode = True
        schema_extra = {
            "example" : {
            "users_id" : 1
            }
        }

class AdminId(BaseModel):
    admin_id : int

    class Config :
        orm_mode = True
        schema_extra = {
            "example" : {
                "admin_id" : 1
                }
        }

class SuperAdmin(BaseModel):
    full_name : str
    email : str
    password : str
    phone_number : str
    referral_code : str
    role_id : int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "full_name": "Test Test",
                "email" : "test@example.com",
                "password" : "Test@1234",
                "phone_number" : "+919087654321",
                "referral_code": "qwerty",
                "role_id": "2",
            },
        }

class AdminID(BaseModel):
    admin_id : int

    class Config :
        orm_mode = True
        schema_extra = {
            "example" : {
                "admin_id" : 1
                }
            }