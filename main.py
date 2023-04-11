from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database.connection import get_db, engine,Base
from core.jwt import auth_handler
from core.jwt.auth_bearer import JWTBearer
from core.api.sales_person import crud,schema, models
from core.api.merchant import models


Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/sales_person_reg", status_code = 200, tags = ["Sales Person"])
async def registration(data:schema.UserCreate, db : Session = Depends(get_db)):
    if data.role_id ==6:
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
        if db_phone is None:
            if not crud.validate_phone_number(data.phone_number, data.country_code):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "Error",                                         
                        "status_code": 400,
                        "data": None,
                        "error": {
                            "status_code": 400,
                            "status": "Error",
                            "message": "Enter a valid phone number."
                        }
                    }
                )
            elif not crud.validate_password(data.password):
                raise HTTPException(                                                                                       
                    status_code=400,
                    detail={
                        "status": "Error",
                        "status_code": 400,
                        "data": None,
                        "error": {
                            "status_code": 400,
                            "status": "Error",
                            "message": """Password must be at least 8 characters long, contains atleast one lower case character, one 
                            upper case character, one digit and one special case character."""
                        }
                    }
                )
         
            else:                                                                                  
                user_reg= crud.create_user(db, data)
                return {
                "detail": {
                            "status": "Success",
                            "status_code": 201,
                            "data": {
                                "status_code": 201,
                                "status": "Success",         
                                "message": "User registered Successfully",                                                                                                                                                                                                                                        
                            "error": None
                        }
                    }
            }

    else:
        raise HTTPException(
                status_code=500,
                detail={
                    "status": "Error",
                    "status_code": 500,
                    "data": None,                                                                                                                                                                                                                                                                                                                                                
                    "error": {
                        "status_code": 500,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                        "status": "Error",                        
                        "message": "Registration only allowed to sales person"
                    }
                }
         )                                                                                                                                                   
@app.post("/login", status_code = 200, tags = ["Sales Person"])                                                                                                                                                                                                                                                                                                                                                                                                                             
async def sales_person_login(data:schema.Login, db : Session = Depends(get_db)):
    verify_user = crud.verify_email_password(db=db, email=data.email, password=data.password)
    if verify_user:
        token = auth_handler.encode_token(verify_user.email)                                          
        refresh_token = auth_handler.refresh_token(verify_user.email)                                          
        users_id = verify_user.__dict__['id']                  
        # users_role = verify_user.__dict__['user_role']                                                                                                                                                                                                    
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
                                # "role":users_role,
                               
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
    
@app.get('/logout', dependencies=[Depends(JWTBearer())], tags = ["Sales Person"])
def logout(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.check_email(db=db, email=email['sub'])    
    if userdata:
        db.expire_all()
        return {
                "detail": {
                        "status": "Success",
                        "status_code": 200,
                        "data": {
                            "status_code": 200,
                            "status": "Success",
                                "message": "User Logged out Successfully",
                        }
            }
        }       



"""api for start time tracking"""
@app.post('/start', dependencies=[Depends(JWTBearer())], tags = ["Sales Person"])
async def start(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_id= userdata.__dict__['id']
    # user_email= userdata.__dict__['email']
    if userdata:
        track_login = crud.track_login(db=db, users_id=users_id)
        if track_login:
                return {
                    "detail": {
                        "status": "Success",
                        "status_code": 200,
                        "data": {
                            "status_code": 200,
                            "status": "Success",
                                "message": "login time tracked  Successfully", 
                        }
                    }
                } 

"""api for end time tracking"""            
@app.post('/stop', dependencies=[Depends(JWTBearer())], tags = ["Sales Person"])   
async def stop(hours:int, minutes:int,token = Depends(JWTBearer()), db : Session=Depends(get_db)): 
    email = auth_handler.decode_token(token=token)
    userdata = crud.get_user_by_email(db=db, email=email['sub'])
    users_id= userdata.__dict__['id']
    # user_email= userdata.__dict__['email']
    if userdata:
        active_period= crud.get_duration(db=db, users_id=users_id, hours=hours, minutes=minutes)
        
        if active_period:
            return {
                    "detail": {
                        "status": "Success",
                        "status_code": 200,
                        "data": {
                            "status_code": 200,
                            "status": "Success",
                                "message": "logout time tracked  Successfully", 
                        }
                    }
                }
        




         
       


