#import requests
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.api.sales_person import crud
from core.database.connection import get_db
from core.jwt import auth_handler
from core.jwt.auth_bearer import JWTBearer
from core.api.admin.crud import get_sales_person, display_sales_person

router = APIRouter()




@router.post("/user_email_login", tags=["Sales Person"])
def user_email_login(role : int, db:Session=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login for sales person, admin and super admin

    """
    check_user = crud.get_user_by_email(db=db, email=form_data.username)
    if not check_user or check_user.__dict__['deleted']==True:    
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "Message" : "Email not found!"
                }
            }
        )
    elif check_user.__dict__['blocked']==True:
            raise HTTPException(
            status_code=401,
            detail={
                "status" : "Error",
                "status_code" : 401,
                "data" : None,
                "error" : {
                    "status_code":401,
                    "status":'Error', 
                    "message" : "User is blocked!"
                }
            }
        )
    else:
        verify_user_role = crud.get_user_roles(db=db, users_id=check_user.__dict__['id'], role=role)
        if not verify_user_role:
            raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Entered user role not found!"
                }
            }
        )
        else:    
            verify_password = crud.verify_email_password(db=db, email=form_data.username, password=form_data.password)

            if not verify_password:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "status" : "Error",
                        "status_code" : 401,
                        "data" : None,
                        "error" : {
                            "status_code":401,
                            "status":'Error', 
                            "Message" : "Login failed! Invalid credentials"
                        }
                    }
                )
            else:
                userinfo = crud.verify_email_password(db=db, email=form_data.username, password=form_data.password)
                if userinfo:
                    if verify_user_role.role_id == 2:
                        last_login = crud.update_last_login(db = db, users_id = check_user.__dict__['id'])
                    token = auth_handler.encode_token(form_data.username)
                    refresh_token = auth_handler.refresh_token(form_data.username)
                    response_msg = {
                        "detail": {
                            "status": "Success",
                            "status_code": 200,
                            "data": {
                                "status_code": 200,
                                "status": "Success",
                                "message": "Login successfully",
                                "access_token": token, "token_type": "bearer",
                                "refresh_token": refresh_token, "token_type": "bearer",
                                "id":userinfo.id,
                                "full_name": userinfo.__dict__['full_name'],
                                "email": userinfo.__dict__['email'],
                                "phone_number": userinfo.__dict__['phone_number']
                            },
                            "error": None
                        }
                    }
                    return response_msg


@router.post('/user/logout', tags=["Sales Person"])
async def logout(token = Depends(JWTBearer()), db : Session = Depends(get_db)):
    """
    Logout for sales person, admin and super admin

    """
    token = auth_handler.decode_token(token=token)
    user = crud.get_user_by_email(db, token['sub'])
    if user :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status" : "success",
                    "message" : "Logout"
                },
                "error": None
            }
        }
        return response_msg
    else :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Invalid User"
                }
            }
        )
    
@router.get("/sales-person-profile", tags = ["Sales Person"])
async def sales_person_profile(token = Depends(JWTBearer()), db : Session = Depends(get_db)):
    """
    Profile view for sales person

    """
    token = auth_handler.decode_token(token=token)
    user = crud.get_user_by_email(db, token['sub'])
    if  not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "User not found"
                }
            }
        )
    verify_user_role = crud.get_user_roles(db=db, users_id=user.id, role=6)
    if not verify_user_role:
        raise HTTPException(
        status_code=400,
        detail={
            "status" : "Error",
            "status_code" : 400,
            "data" : None,
            "error" : {
                "status_code":400,
                "status":'Error', 
                "message" : "Only sales person can view"
            }
        }
    )
    sales_person = get_sales_person(db = db, users_id = user.id)
    if not sales_person:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person profile not exist"
                }
            }
        )
    profile = display_sales_person(db = db, sales_person_id = sales_person.id)
    if profile:
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status" : "success",
                    "message" : "Sales person profile",
                    "profile" : profile
                },
                "error": None
            }
        }
        return response_msg
    else :
        raise HTTPException(
            status_code=500,
            detail={
                "status" : "Error",
                "status_code" : 500,
                "data" : None,
                "error" : {
                    "status_code":500,
                    "status":'Error', 
                    "message" : "internal server error."
                }
            }
        )
    

@router.get("/display-merchant-stages", tags = ["Sales Person"])
async def display_all_merchant_stages(db: Session = Depends(get_db)):

    """ Disaplay all merchant stages """

    mer_stages = crud.display_all_merchant_stages(db = db)
    if not mer_stages :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "No data ! There is no merchant stages"
                },
                "error": None
            }
        }
        return response_msg
    elif mer_stages :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Merchant stages",
                    "merchant_stages" : mer_stages
                },
                "error": None
            }
        }
        return response_msg
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "status" : "Error",
                "status_code" : 500,
                "data" : None,
                "error" : {
                    "status_code":500,
                    "status":'Error',
                    "message" : "internal server error."
                }
            }
        )


@router.post('/start-time-logged', dependencies=[Depends(JWTBearer())], tags=["Sales Person"])
async def start_time_logged(start:str, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    """ Sales persons active login time tracking """

    payload = auth_handler.decode_token(token)
    userdata = crud.get_user_by_email(db=db, email=payload['sub'])

    if not userdata:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "Error",
                "status_code": 404,
                "data": None,
                "error": {
                    "status_code": 404,
                    "status": "Error",
                    "message": "No user found",
                }
            },
        )
    if start == "true":
        time_track = crud.start_time_tracking(db=db,user_id=userdata.__dict__['id'])
        if time_track == False:
            raise HTTPException(
                status_code=409,
                detail={
                    "status": "Error",
                    "status_code": 409,
                    "data": None,
                    "error": {
                        "status_code": 409,
                        "status": "Error",
                        "message": "Error while starting",
                    }
                },
            )
        elif time_track:
            response_msg = {
                "detail": {
                    "status": "Success",
                    "status_code": 200,
                    "data": {
                        "status_code": 200,
                        "status": "Success",
                        "message": "Active login started",
                        "user_id" : time_track.users_id,
                        "stat_time": time_track.log_in_time
                    },
                    "error": None
                }
            }
            return response_msg


        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "Error",
                    "status_code": 500,
                    "data": None,
                    "error": {
                        "status_code": 500,
                        "status": 'Error',
                        "message": "internal server error."
                    }
                }
            )



@router.post('/end-time-logged', dependencies=[Depends(JWTBearer())], tags=["Sales Person"])
async def end_time_logged(end:str, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    """Sales person active-logout time """

    payload = auth_handler.decode_token(token)
    userdata = crud.get_user_by_email(db=db, email=payload['sub'])

    if not userdata :
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code": 404,
                "data": None,
                "error": {
                    "status_code": 404,
                    "status": "Error",
                    "message": "Invalid user"
                }
            }
        )
    if end == "true":
            end_trcaking = crud.end_time_tracking(db=db,user_id=userdata.__dict__['id'])
            if not end_trcaking:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "status": "Error",
                        "status_code": 409,
                        "data": None,
                        "error": {
                            "status_code": 409,
                            "status": "Error",
                            "message": "Error while ending",
                        }
                    },
                )
            elif end_trcaking:
                response_msg = {
                    "detail": {
                        "status": "Success",
                        "status_code": 200,
                        "data": {
                            "status_code": 200,
                            "status": "Success",
                            "message": "Active login stopped"
                        },
                        "error": None
                    }
                }
                return response_msg

            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "status": "Error",
                        "status_code": 500,
                        "data": None,
                        "error": {
                            "status_code": 500,
                            "status": 'Error',
                            "message": "internal server error."
                        }
                    }
                )
            

@router.get("/active-login",dependencies=[Depends(JWTBearer())], tags=["Sales Person"])
async def list_of_all_time_log(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    """ list of all time logs for a sales person"""
    payload = auth_handler.decode_token(token)
    userdata = crud.get_user_by_email(db=db, email=payload['sub'])

    if not userdata:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "Error",
                "status_code": 404,
                "data": None,
                "error": {
                    "status_code": 404,
                    "status": "Error",
                    "message": "Invalid user"
                }
            }
        )
    active_log = crud.list_time_logs_for_salesperson(db=db,user_id=userdata.__dict__['id'])
    if not active_log :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "No data ! There is no time log data"
                },
                "error": None
            }
        }
        return response_msg
    elif active_log :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Active time log",
                    "time_log" : active_log
                },
                "error": None
            }
        }
        return response_msg
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "status" : "Error",
                "status_code" : 500,
                "data" : None,
                "error" : {
                    "status_code":500,
                    "status":'Error',
                    "message" : "internal server error."
                }
            }
        )
    
@router.get("/get-team-members", tags = ["Sales Person"])
async def get_team_members(skip : int = 0, limit: int = 10, token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    token = auth_handler.decode_token(token=token)
    user = crud.get_user_by_email(db, token['sub'])
    if  not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "User not found"
                }
            }
        )
    sales_person = get_sales_person(db = db, users_id = user.id)
    if not sales_person:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person profile not exist"
                }
            }
        )
    team_members = crud.get_sales_person_team_members(db = db, users_id = user.id)
    if team_members:
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status" : "success",
                    "message" : "Team members",
                    "team_members" : team_members,
                    "pagination" :{
                        "limit" : limit,
                        "skip" : skip,
                        "count" : len(list(team_members)),
                        "data_count" : len(list(team_members)[skip : skip + limit])
                    },
                    "sort" : {
                        "sort_by" :  "Not sorted"
                    },
                },
                "error": None
            }
        }
        return response_msg
    else :
        raise HTTPException(
            status_code=500,
            detail={
                "status" : "Error",
                "status_code" : 500,
                "data" : None,
                "error" : {
                    "status_code":500,
                    "status":'Error', 
                    "message" : "internal server error."
                }
            }
        )
