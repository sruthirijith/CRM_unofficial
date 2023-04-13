from fastapi import APIRouter, Depends, HTTPException, Response, Form, UploadFile
from sqlalchemy.orm import Session
from typing import Any

from core.api.admin import schema
from core.api.admin import crud
from core.api.super_admin.schema import UserId
from core.api.sales_person.crud import (
                                check_role,
                                get_user_by_id,
                                check_if_user_exists,
                                get_user_by_phonenumber,
                                validate_phone_number,
                                create_user,
                                get_user_roles
                                 )
from core.database.connection import get_db, get_mongo_db
from core.jwt.auth_bearer import JWTBearer
from core.jwt import auth_handler
from core.api.super_admin.crud import display_admin_profile


router = APIRouter()

@router.post("/register", status_code=201, tags=["Admin"])
async def create_user_api(users: schema.UserCreate, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    Register sales person
    
    """
    crud.check_admin(db, token)
    if users.role_id in [6]:
        reg_email : Any = check_if_user_exists(db = db, email = users.email)
        if reg_email :
            raise HTTPException(
                status_code=409,
                detail = {
                    "status" : "Error",
                    "status_code" : 409,
                    "data" : None,
                    "error" : {
                        "status_code":409,
                        "status":'Error', 
                        "message": "Email already registered",
                    }
                }
            )

        reg_phone: Any = get_user_by_phonenumber(db, phone_number=users.phone_number)
        if reg_phone:
            raise HTTPException(
                status_code=409,
                detail = {
                    "status" : "Error",
                    "status_code" : 409,
                    "data" : None,
                    "error" : {
                        "status_code":409,
                        "status":'Error', 
                        "message": "Phone number already registered",
                    }
                }
            )

        if reg_phone is None:

            if not validate_phone_number(users.phone_number, users.country_code):
                raise HTTPException(
                    status_code=400,
                    detail = {
                        "status" : "Error",
                        "status_code" : 400,
                        "data" : None,
                        "error" : {
                            "status_code":400,
                            "status":'Error', 
                            "message": "Enter a valid phone number."
                        }
                    }
                )

            created_user, role = create_user(db, users)
            response_msg = {
                "detail": {
                    "status": "Success",
                    "status_code": 200,
                    "data": {
                        "status_code": 200,
                        "status": "Success",
                        "Message": "User registred Successfully",
                        "id" : created_user.id,
                        "full_name" : created_user.full_name,
                        "email": created_user.email,
                        "phonenumber": created_user.phone_number,
                        "role": role.role_id,
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
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message": "Only sales person can register"
                }
            }
        )

@router.post("/create_sales_person", tags=["Admin"])
async def create_sales_person(sales_person: schema.CreateSalesPerson, token = Depends(JWTBearer()), db : Session = Depends(get_db)):
    """
    Create sales person
    
    """
    crud.check_admin(db, token)
    user = crud.get_user_by_id(db = db, user_id = sales_person.users_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "User id not match"
                }
            }
        )
    sales_person_profile = crud.get_sales_person(db = db, users_id = sales_person.users_id)
    if sales_person_profile :
        raise HTTPException(
            status_code=409,
            detail={
                "status" : "Error",
                "status_code" : 409,
                "data" : None,
                "error" : {
                    "status_code":409,
                    "status":'Error', 
                    "message" : "Sales person already exist"
                }
            }
        )
    sales_person_creation = crud.create_sales_person(db = db, users_id = sales_person.users_id, sales_person = sales_person)
    if sales_person_creation :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Sales person created successfully",
                    "sales_person" : sales_person_creation.id
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

@router.get("/display_all_sales_person", tags=["Admin"])
async def display_all_sales_person(skip : int = 0, limit: int = 10, token = Depends(JWTBearer()), db : Session = Depends(get_db)):

    crud.check_admin(db, token)
    users = crud.get_user_sales_person(db = db)
    user_id = []
    for i in users:
        for j in i:
            user_id.append(j)
    sales_person_profile = crud.display_all_sales_person(db = db, users_id = user_id)
    response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Sales person profiles",
                    "profile" : sales_person_profile[skip : skip + limit],
                    "pagination" :{
                        "limit" : limit,
                        "skip" : skip,
                        "count" : len(list(sales_person_profile)),
                        "data_count" : len(list(sales_person_profile)[skip : skip + limit])
                    },
                    "sort" : {
                        "sort_by" : "Sort by store id",
                    }, 
                },
                "error": None
            }
        }
    return response_msg

@router.put("/update_sales_person", tags=["Admin"])
async def update_sales_person(sales_person : schema.UpdateSalesPerson, token = Depends(JWTBearer()), db : Session = Depends(get_db)):

    crud.check_admin(db, token)
    if not sales_person.sales_person_id :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Sales person id not given"
                }
            }
        )
    sales_person_profile = crud.get_sales_person_id(db = db, sales_person_id = sales_person.sales_person_id)
    if not sales_person_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person not exist"
                }
            }
        )
    profile_data = sales_person.dict(exclude_unset=True)
    del profile_data['sales_person_id']
    update_profile = crud.update_sales_person(db = db, sales_person_id = sales_person_profile.id, sales_person = profile_data, users_id = sales_person_profile.users_id)
    if update_profile :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Sales person updated successfully",
                    "sales_person" : sales_person_profile.id
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

@router.post("/change_password", tags=["Admin"])
async def change_password(sales_person : schema.SalesPersonId, token = Depends(JWTBearer()), db : Session = Depends(get_db)):

    crud.check_admin(db, token)
    if not sales_person.sales_person_id :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Sales person id not given"
                }
            }
        )
    sales_person_profile = crud.get_sales_person_id(db = db, sales_person_id = sales_person.sales_person_id)
    if not sales_person_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person not exist"
                }
            }
        )
    user = crud.get_user_by_id(db = db, user_id = sales_person_profile.users_id)
    change_password = crud.update_password(db = db, users_id = sales_person_profile.users_id, email = user.email)
    if change_password :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": f"Password Changed and New password send to {user.email}",
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
    
@router.post("/display_sales_person", tags = ['Admin'])
async def display_sales_person(sales_person : schema.SalesPersonId, token = Depends(JWTBearer()), db : Session = Depends(get_db)):

    crud.check_admin(db, token)
    if not sales_person.sales_person_id :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Sales person id not given"
                }
            }
        )
    profile = crud.display_sales_person(db = db, sales_person_id = sales_person.sales_person_id)
    if profile:
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Sales person profiles",
                    "profile" : profile
                },
                "error": None
            }
        }
        return response_msg
    elif profile == [] :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Nothing to display"
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

@router.post("/profile-image-upload", dependencies=[Depends(JWTBearer())], tags=["Admin"])
async def profile_image_upload(file_upload : UploadFile, file_collection : str = Form(), source_id : int = Form(), sales_person_id : int = Form()\
                        , token = Depends(JWTBearer()), db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):
    
    crud.check_admin(db, token)
    sales_person_profile = crud.get_sales_person_id(db = db, sales_person_id = sales_person_id)
    if not sales_person_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person not exist"
                }
            }
        )
    user = crud.get_user_by_id(db = db, user_id = sales_person_profile.users_id)
    if file_collection not in ('sppi'):
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "only sales person image can upload",
                }
            },
        )

    if not user:
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "Invalid User",
                }
            },
        )
    
    file_name = file_collection + "_" + str(source_id)
    file_content = await file_upload.read()
    file_types = file_upload.content_type
    file_type_split = str(file_types).split('/')
    if 'image' != file_type_split[0]:
        raise HTTPException (
            status_code = 400,
            detail = {
                "status": "Error",
                "status_code" : 400,
                "data": None,
                "error" : {
                    "status_code" : 400,
                    "status":"Error",
                    "message" : "only image can upload",
                }
            }
        )
    if len(file_content) <= 0:
        raise HTTPException (
            status_code = 400,
            detail = {
                "status": "Error",
                "status_code" : 400,
                "data": None,
                "error" : {
                    "status_code" : 400,
                    "status":"Error",
                    "message" : "No file",
                }
            }
        )
    elif len(file_content) >= 6000000:
        raise HTTPException (
            status_code = 413,
            detail = {
                "status": "Error",
                "status_code" : 413,
                "data": None,
                "error" : {
                    "status_code" : 413,
                    "status":"Error",
                    "message" : "Image size must be less than 6 mb",
                }
            }
        )
    content_type = file_upload.content_type
    result = crud.save_file(mongo_db, file_collection, file_name, file_content, content_type)
    if not result:
        raise HTTPException (
            status_code = 500,
            detail = {
                "status": "Error",
                "status_code" : 500,
                "data": None,
                "error" : {
                    "status_code" : 500,
                    "status":"Error",
                    "message" : "File upload failed",
                }
            },
        )
    
    if file_collection == 'sppi':
        image_path = {'profile_image' : str(result)}
        update_profile_image = crud.update_profile(db =db, user_id= user.__dict__['id'],update_data=image_path)
        if update_profile_image > 0:

            print("success")
        else:
            print("failed no consumer")


    return {
        "detail": {
            "status": "Success",
            "status_code": 200,
            "data": {
                "status_code": 200,
                "status": "Success",
                "message": "File uploaded Successfully",
                "file_id": str(result)
            },
            "error": None
        }
    }

@router.get("/profile-image-download/{file_collection}/{file_id}", tags=["Admin"])
async def profile_image_download(file_collection : str ,file_id : str, mongo_db = Depends(get_mongo_db)):

    if file_collection not in ('sppi'):
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "Not found",
                }
            },
        )
    
    exists = crud.check_if_file_exists(mongo_db, file_collection, file_id)
    if not exists:
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "File doesn't exist",
                }
            },
        )
        
    result = crud.retrieve_file(mongo_db, file_collection, file_id)
    if not result:
        raise HTTPException (
            status_code = 500,
            detail = {
                "status": "Error",
                "status_code" : 500,
                "data": None,
                "error" : {
                    "status_code" : 500,
                    "status":"Error",
                    "message" : "File download failed",
                }
            },
        )
      
    # return {
    #     "detail": {
    #         "status": "Success",
    #         "status_code": 200,
    #         "data": {
    #             "status_code": 200,
    #             "status": "Success",
    #             "message": "File downloaded Successfully",
    #             "content": result
    #         },
    #         "error": None
    #     }
    # }
    return Response(status_code=200, content=result)

@router.delete("/profile-image-delete/{file_collection}", dependencies=[Depends(JWTBearer())], tags=["Admin"])
async def profile_image_delete(file_collection : str,sales_person_id : int, token = Depends(JWTBearer()), db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):

    crud.check_admin(db, token)
    if not sales_person_id :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Sales person id not given"
                }
            }
        )
    sales_person_profile = crud.get_sales_person_id(db = db, sales_person_id = sales_person_id)
    if not sales_person_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person not exist"
                }
            }
        )

    if file_collection not in ('sppi'):
        raise HTTPException (
            status_code = 400,
            detail = {
                "status": "Error",
                "status_code" : 400,
                "data": None,
                "error" : {
                    "status_code" : 400,
                    "status":"Error",
                    "message" : "only sales person image can delete",
                }
            },
        )

    sales_person_profile = crud.get_sales_person_id(db=db, sales_person_id=sales_person_profile.id)
    if file_collection == 'sppi':
        if not sales_person_profile:
            raise HTTPException (
                status_code = 404,
                detail = {
                    "status": "Error",
                    "status_code" : 404,
                    "data": None,
                    "error" : {
                        "status_code" : 404,
                        "status":"Error",
                        "message" : "Invalid sales person profile",
                    }
                },
            )
        file_id = sales_person_profile.profile_image

        exists = crud.check_if_file_exists(mongo_db, file_collection, file_id)
        if not exists:
            raise HTTPException (
                status_code = 404,
                detail = {
                    "status": "Error",
                    "status_code" : 404,
                    "data": None,
                    "error" : {
                        "status_code" : 404,
                        "status":"Error",
                        "message" : "File doesn't exist",
                    }
                },
            )
        result = crud.delete_file(mongo_db, file_collection, file_id)
        if not result:
            raise HTTPException (
                status_code = 500,
                detail = {
                    "status": "Error",
                    "status_code" : 500,
                    "data": None,
                    "error" : {
                        "status_code" : 500,
                        "status":"Error",
                        "message" : "File deletion failed",
                    }
                },
            )
        update_data = {"profile_image" : None}
        update_profile_info = crud.update_profile(db=db, user_id= sales_person_profile.users_id, update_data= update_data)
        if not update_profile_info:
            raise HTTPException (
                status_code = 400,
                detail = {
                    "status": "Error",
                    "status_code" : 400,
                    "data": None,
                    "error" : {
                        "status_code" : 400,
                        "status":"Error",
                        "message" : "File updation in profile failed and image deleted",
                    }
                }
            )
        return {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "File deleted Successfully",
                },
                "error": None
            }
        }

    

@router.put("/block-sales-person", tags = ['Admin'])
async def block_sales_person(sales_person : schema.SalesPersonId,token = Depends(JWTBearer()), db: Session = Depends(get_db)):

    crud.check_admin(db, token)
    user_sales_person = crud.get_sales_person_id(db = db, sales_person_id = sales_person.sales_person_id)
    if not user_sales_person:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person not exist"
                }
            }
        )
    user = get_user_by_id(db = db, user_id = user_sales_person.users_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "User not exist"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)
    if not role.role_id == 6 :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Only for sales person"
                }
            }
        )
    if user.blocked == True :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : f"{sales_person.sales_person_id} is a blocked user"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)
    if role.__dict__['role_id'] in [1] :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Can not block super admin"
                }
            }
        )
    block_user = crud.update_block_user(db = db, users_id = user.id, block = True)
    if block_user :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": f"{sales_person.sales_person_id} is blocked"
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
    
@router.put("/unblock-sales-person", tags = ['Admin'])
async def unblock_sales_person(sales_person : schema.SalesPersonId,token = Depends(JWTBearer()), db: Session = Depends(get_db)):

    crud.check_admin(db, token)
    user = crud.get_sales_person_id(db = db, sales_person_id = sales_person.sales_person_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Sales person not exist"
                }
            }
        )
    user = get_user_by_id(db = db, user_id = user.users_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "User not exist"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)
    if not role.__dict__['role_id'] in [6] :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Only for sales person"
                }
            }
        )
    if user.blocked == False :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : f"{sales_person.sales_person_id} is a unblocked user"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)
    if role.__dict__['role_id'] in [1] :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Can not unblock super admin"
                }
            }
        )
    block_user = crud.update_block_user(db = db, users_id = user.id, block = False)
    if block_user :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": f"{sales_person.sales_person_id} is unblocked"
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
    
@router.get("/list-blocked-sales-person", tags = ["Admin"])
async def list_blocked_sales_person(skip : int = 0, limit: int = 10, token = Depends(JWTBearer()), db: Session = Depends(get_db)):

    crud.check_admin(db, token)
    user_id = crud.get_users_id_from_roles(db = db)
    user_profile = []
    for i in user_id:
        for j in i:
            user_profile.append(j)
    profile = crud.display_blocked_sales_person(db = db, users_id = user_profile)
    if not profile :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "There is no blocked users"
                },
                "error": None
            }
        }
        return response_msg
    elif profile:
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "List of blocked sales person",
                    "profile" : profile[skip : skip + limit]
                },
                "pagination" :{
                        "limit" : limit,
                        "skip" : skip,
                        "count" : len(list(profile)),
                        "data_count" : len(list(profile)[skip : skip + limit])
                    },
                    "sort" : {
                        "sort_by" : "Sort by store id",
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

@router.get("/admin-profile", tags = ["Admin"])
async def admin_profile(token = Depends(JWTBearer()), db: Session = Depends(get_db)):
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
    verify_user_role = get_user_roles(db = db, users_id = user.id, role = 2)
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
                    "message" : "Only Admin can view"
                }
            }
        )
    admin = display_admin_profile(db = db, users_id = user.id)
    if admin :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status" : "success",
                    "message" : "Sales person profile",
                    "profile" : admin
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
    

@router.get("/list-time-log",dependencies=[Depends(JWTBearer())], tags=["Admin"])
async def list_of_time_log(token = Depends(JWTBearer()), db : Session=Depends(get_db)):
    """ list of all time logs """
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
    active_log = crud.list_time_logs(db=db)
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