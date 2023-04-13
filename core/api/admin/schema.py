from typing import Optional, Text
from datetime import date
from pydantic import BaseModel, EmailStr, Field


class UsersBase(BaseModel):
    full_name: str = Field(..., max_length=100, description="Full name")
    email: EmailStr = Field(..., description="user email")
    phone_number: str = Field(..., min_length=5, max_length=20, description="Phone number")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "full_name": "Test Test",
                "email" : "test@example.com",
                "phone_number" : "+911234567890",
            },
        }

        
class UserRoles(BaseModel):
    role: str = Field(..., min_length=1, max_length=20, description="User role")
    description: str = Field(..., min_length=5, max_length=500, description="User role description")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "role": "admin",
                "description": "admin"
            },
        }   


class UserCreate(UsersBase):
    country_code: Optional[str]
    referred_by: Optional[str]
    role_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "country_code": "+91",
                "referred_by": "abcdef",
                "role_id": "6",
                "full_name": "Test Test",
                "email" : "test@example.com",
                "phone_number" : "+911234567890",
            },
        }     


class Users(BaseModel):
    full_name : Optional[str]
    email : Optional[EmailStr]
    password : Optional[str]
    phone_number : Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Test Test",
                "email": "test@example.com",
                "password": "Test@123",
                "phone_number": "+911234567890"
            },
        }     

class LoginSchema_email(BaseModel):

    email : Optional[EmailStr]

    class Config:
        schema_extra = {
            "example": {
                "email": "test@example.com"
            },
        } 

class LoginSchema_phonenumber(BaseModel):

    phone_number : str

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "+911234567890",
            },
        } 

class Token(BaseModel):
    access_token : str
    token_type : str


class TokenData(BaseModel):
    username : str 

    class Config:
        schema_extra = {
            "example": {
                "username": "test",
            },
        } 

class Otp(BaseModel):
    otp : str
    key : str
    phone_number : str

    class Config:
        schema_extra = {
            "example": {
                "otp": "12345",
                "key": "qweertyuiopasdfghjkl",
                "phone_number": "+911234567890"
            },
        } 

class UserOut(BaseModel):
    full_name: str = Field(..., max_length=100, description="Full name")
    email: EmailStr = Field(..., description="user email")
    phone_number: str = Field(..., min_length=5, max_length=20, description="Phone number")

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Test Test",
                "email": "test@example.com",
                "phone_number": "+911234567890"
            },
        } 
    
class Change_pin(BaseModel):
    old_pin : str = Field(..., max_length = 200, description = "Existing pin")
    new_pin : str = Field(..., max_length = 200, description = "New pin")
    reenter_pin :str = Field(..., max_length = 200, description = "Reenter pin")

    class Config:
        schema_extra = {
            "example": {
                "old_pin": "1234",
                "new_pin": "0000",
                "reenter_pin": "0000"
            },
        } 
    
class Change_password(BaseModel):
    old_password: str = Field(..., max_length=200, description="Existing Password")
    new_password: str = Field(..., max_length=200, description="New Password")
    reenter_password: str = Field(..., max_length=200, description="Reenter Password")

    class Config:
            schema_extra = {
                "example": {
                    "old_password": "Test@123",
                    "new_password": "Abcd@1234",
                    "reenter_password": "Abcd@1234"
                },
            }      

class Add_Pin(BaseModel):
    pin : str
    reenter_pin : str

    class Config:
        schema_extra = {
            "example": {
                "pin": "1234",
                "reenter_pin": "1234"
            },
        }  

class GenerateOtp(BaseModel):
    phone_number: str
    channel: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "+911234567890",
                "channel": "sms"
            },
        }   

class VerifyOtp(BaseModel):
    phone_number: str
    otp: str

    class Config:
        schema_extra = {
            "example": {
                "phone_number": "+911234567890",
                "otp": "12345"
            },
        }

class CreateSalesPerson(BaseModel):
    users_id : int
    dob : date
    gender : int
    address1 : str
    address2 : str
    city : str
    district : str
    state : str
    country : str
    postal_code : str
    designation : str

    class Config:
        schema_extra = {
            "example": {
                "users_id": "1",
                "dob" :  "1995-02-06",
                "gender" : 1,
                "address1" : "address",
                "address2" : "address",
                "city" : "city",
                "district" : "district",
                "state" : "state",
                "country" : "country",
                "postal_code" : "987654",
                "designation" : "sales person"
            },
        }

class UpdateSalesPerson(BaseModel):
    sales_person_id : Optional[int]
    full_name : Optional[str]
    dob : Optional[date]
    gender : Optional[int]
    address1 : Optional[str]
    address2 : Optional[str]
    city : Optional[str]
    district : Optional[str]
    state : Optional[str]
    country : Optional[str]
    postal_code : Optional[str]
    designation : Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "sales_person_id": "1",
                "full_name" : 'test',
                "dob" :  "1995-02-06",
                "gender" : 1,
                "address1" : "address",
                "address2" : "address",
                "city" : "city",
                "district" : "district",
                "state" : "state",
                "country" : "country",
                "postal_code" : "987654",
                "designation" : "sales person"
            },
        }

class SalesPersonId(BaseModel):
    sales_person_id : Optional[int]

    class Config :
        schema_extra = {
            "example" : {
            "sales_person_id" : 1
            }
        }