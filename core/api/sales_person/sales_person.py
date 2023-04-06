from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database.connection import get_db, engine,Base
from core.jwt import auth_handler
from core.jwt.auth_bearer import JWTBearer
import schema, crud


Base.metadata.create_all(bind=engine)
router = APIRouter()

@router.post("/sales_person_reg", status_code = 200, tags = ["Sales Person"])
async def registration(data:schema.registration, db : Session = Depends(get_db)):
    db_user = crud.check_email(db=db, email=data.email)
    if db_user:
         raise HTTPException(
                    status_code=200,
                    detail={
                        "status": "Error",
                        "status_code": 200,
                        "data": None,
                        "error": {
                            "status_code": 200,
                            "status": "Error",
                            "message": "Email already registered"
                        }
                    }
                )
    db_phone = crud.check_phone(db=db, phone_number=data.phone_number)
    if db_phone:
          raise HTTPException(
                status_code=200,
                detail={
                    "status": "Error",
                    "status_code": 200,
                    "data": None,
                    "error": {
                        "status_code": 200,
                        "status": "Error",
                        "message": "Phone number already registered"
                    }
                }
            )
    else:
         return {
                "detail": {
                            "status": "Success",
                            "status_code": 201,
                            "data": {
                                "status_code": 201,
                                "status": "Success",
                                "message": "User registered Successfully",
                                
                            },
                            "error": None
                        }
                    }
         
@router.post("/login", status_code = 200, tags = ["Sales Person"]) 
async def sales_person_login(data:schema.Login, db : Session = Depends(get_db)):
    verify_user = crud.verify_email_password(db=db, email=data.email, password=data.password)
    if verify_user:
        token = auth_handler.encode_token(verify_user.email)
        refresh_token = auth_handler.refresh_token(verify_user.email)
        users_id = verify_user.__dict__['id']
        users_role = verify_user.__dict__['user_role']
        return {
                "detail": {
                        "status": "Success",
                        "status_code": 200,
                        "data": {
                            "status_code": 200,
                            "status": "Success",
                                "message": "User Logged in Successfully",
                                "access_token": token, "token_type": "bearer",
                                "refresh_token": refresh_token, "token_type": "bearer",
                               
                                "email": verify_user.__dict__['email'],
                                "users_id":users_id,
                                "role":users_role,
                               
                            },
                            "error": None
                        }
                    }
    else:
        raise HTTPException(
                    status_code = 401, 
                    detail={
                        "status": "Error",
                        "status_code": 401,
                        "data": None,
                        "error": {
                            "status_code": 401,
                            "status": "Error",
                            "message": "Login failed! Invalid credentials"
                        }
                    }
                )