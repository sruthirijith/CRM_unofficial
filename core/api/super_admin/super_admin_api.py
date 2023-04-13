from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Response,  Form, UploadFile
from sqlalchemy.orm import Session

from core.api.super_admin import schema
from core.api.super_admin import crud
from core.api.sales_person.crud import ( get_user_by_email,
                                 get_user_by_phonenumber,
                                 validate_phone_number,
                                 check_role,
                                 get_user_by_id)
from core.database.connection import get_db, get_mongo_db
from core.utils import password
from core.utils.password import validate_password
from core.jwt import auth_handler
from core.jwt.auth_bearer import JWTBearer
from core.api.admin.schema import UserCreate

router = APIRouter()

@router.post("/create-super-admin", tags = ["Super Admin"], include_in_schema=False)
async def create_super_admin(user: schema.SuperAdmin, db: Session = Depends(get_db)):
    super_admin = crud.create_superadmin(db = db, user = user)
    return {"Successfully create superadmin"}

@router.post("/create-admin", tags=["Super Admin",])
async def register_admin(user: schema.AdminCreate, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db, token)
    if user.role_id ==2:  
        db_user: Any = get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=409,
                detail={
                    "status" : "Error",
                    "status_code" : 409,
                    "data" : None,
                    "error" : {
                        "status_code":409,
                        "status":'Error', 
                        "message": "Email already registered"
                    }
                }
            )

        reg_phone: Any = get_user_by_phonenumber(db, phone_number=user.phone_number)

        if reg_phone:
            raise HTTPException(
                status_code=409,
                detail={
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
        
            if not validate_phone_number(user.phone_number, user.country_code):
                raise HTTPException(
                    status_code=400,
                    detail={
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
                
            elif not validate_password(user.password):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status" : "Error",
                        "status_code" : 400,
                        "data" : None,
                        "error" : {
                            "status_code":400,
                            "status":'Error', 
                            "message": """Password must be at least 8 characters long, contains atleast one lower case character, one 
                                        upper case character, one digit and one special case character."""
                        }
                    }
                )
                
            created_user, role, create_admin = crud.create_user(db, user)
            response_msg = {
                "detail": {
                    "status": "Success",
                    "status_code": 200,
                    "data": {
                        "status_code": 200,
                        "status": "Success",
                        "message": "Admin created Successfully",
                        "id" : created_user.id,
                        "admin_id" : create_admin.id,
                        "username": created_user.full_name,
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
                    "message": "Only For Admin registration."
                }
            }
        )

@router.get("/display-all-admin", tags = ["Super Admin"])
async def display_admin(skip : int = 0, limit: int = 10, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db, token)
    profile = crud.display_all_admin_profile(db = db)
    if not profile :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "There is no admin profile"
                },
                "error": None
            }
        }
        return response_msg
    elif profile :
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Admin Details",
                    "profiles" : profile[skip : skip + limit],
                    "pagination" :{
                        "limit" : limit,
                        "skip" : skip,
                        "count" : len(list(profile)),
                        "data_count" : len(list(profile)[skip : skip + limit])
                    },
                    "sort" : {
                        "sort_by" : "Sort by store id",
                    },
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

@router.put("/update-admin", tags=["Super Admin",])
async def update_admin(users : schema.UpdateAdminProfile, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db,token)
    user = get_user_by_id(db = db, user_id = users.users_id)
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
                    "message" : f"{users.users_id} not exist"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)
    if role.__dict__['role_id'] in [2] :
        update_data = users.dict(exclude_unset = True)
        profile_update = crud.update_admin_profile(db, user.id, update_data)
        if profile_update :
            response_msg = {
                "detail": {
                    "status": "Success",
                    "status_code": 200,
                    "data": {
                        "status_code": 200,
                        "status": "Success",
                        "message": "Admin profile updated successfully",
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
                        "message" : "Only for admin"
                    }
                }
            )


@router.put("/block-admin", tags=["Super Admin",])
async def block_admin(admin : schema.AdminID,token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db, token)
    admin_profile = crud.check_admin_exist(db, admin.admin_id)
    if not admin_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Admin not exist"
                }
            }
        )
    user = get_user_by_id(db = db, user_id = admin_profile.users_id)
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
                    "message" : f"{admin.admin_id} is a blocked user"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)

    if role.__dict__['role_id'] in [2] :

        block_user = crud.update_block_user(db = db, users_id = user.id, block = True)
        if block_user :
            response_msg = {
                "detail": {
                    "status": "Success",
                    "status_code": 200,
                    "data": {
                        "status_code": 200,
                        "status": "Success",
                        "message": f"{admin.admin_id} is blocked"
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
                        "message" : "Only for admin"
                    }
                }
            )
    
@router.put("/unblock-admin", tags=["Super Admin",])
async def unblock_admin(admin : schema.AdminID,token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db, token)
    admin_profile = crud.check_admin_exist(db, admin.admin_id)
    if not admin_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Admin not exist"
                }
            }
        )
    user = get_user_by_id(db = db, user_id = admin_profile.users_id)
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
                    "message" : f"{admin.admin_id} is a unblocked user"
                }
            }
        )
    role = check_role(db = db, users_id = user.id)

    if role.__dict__['role_id'] in [2] :
        
        block_user = crud.update_block_user(db = db, users_id = user.id, block = False)
        if block_user :
            response_msg = {
                "detail": {
                    "status": "Success",
                    "status_code": 200,
                    "data": {
                        "status_code": 200,
                        "status": "Success",
                        "message": f"{admin.admin_id} is unblocked"
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
                        "message" : "Only for admin"
                    }
                }
            )
    

@router.get("/list-blocked-admin", tags = ["Super Admin"])
async def list_blocked_admin(skip : int = 0, limit: int = 10, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db, token)
    user_id = crud.get_users_id_from_roles(db = db)
    user_profile = []
    for i in user_id:
        for j in i:
            user_profile.append(j)
    profile = crud.display_blocked_admin(db = db, users_id = user_profile)
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
                    "message": "List of blocked admin",
                    "profile" : profile[skip : skip + limit],
                    "pagination" :{
                        "limit" : limit,
                        "skip" : skip,
                        "count" : len(list(profile)),
                        "data_count" : len(list(profile)[skip : skip + limit])
                    },
                    "sort" : {
                        "sort_by" : "Sort by store id",
                    },
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
    
@router.post("/display-admin", tags = ["Super Admin"])
async def display_admin(user : schema.AdminId, token = Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.check_super_admin(db, token)
    admin = crud.check_admin_exist(db = db, admin_id = user.admin_id)
    if not admin :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Admin not exist"
                }
            }
        )
    profile = crud.display_admin_profile(db = db, users_id = admin.users_id)
    if profile:
        response_msg = {
            "detail": {
                "status": "Success",
                "status_code": 200,
                "data": {
                    "status_code": 200,
                    "status": "Success",
                    "message": "Admin profile",
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
    

    
@router.post("/admin-profile-image-upload", tags = ["Super Admin"])
async def admin_profile_image(file_upload : UploadFile,file_collection : str = Form(),source_id : int = Form(),admin_id : int = Form()\
                             , token = Depends(JWTBearer()),  db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):

    crud.check_super_admin(db, token)
    admin_profile = crud.check_admin_by_admin_id(db = db, admin_id = admin_id)
    if not admin_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Admin not exist"
                }
            }
        )

    if file_collection not in ('api'):
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "only admin image can upload",
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
    
    if file_collection == 'api':
        image_path = {'profile_image' : str(result)}
        update_profile_image = crud.update_profile(db =db, user_id= admin_profile.__dict__['users_id'],update_data=image_path)
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

@router.get("/admin-profile-image-download/{file_collection}/{file_id}", tags=["Super Admin"])
async def admin_profile_image_download(file_collection : str ,file_id : str, mongo_db = Depends(get_mongo_db)):

    if file_collection not in ('api'):
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

@router.delete("/admin-profile-image-delete/{file_collection}", dependencies=[Depends(JWTBearer())], tags=["Super Admin"])
async def admin_profile_image_delete(file_collection : str,admin_id : int, token = Depends(JWTBearer()), db : Session=Depends(get_db), mongo_db = Depends(get_mongo_db)):

    crud.check_super_admin(db, token)
    admin_profile = crud.check_admin_by_admin_id(db = db, admin_id = admin_id)
    if not admin_profile :
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Admin not exist"
                }
            }
        )

    if file_collection not in ('api'):
        raise HTTPException (
            status_code = 404,
            detail = {
                "status": "Error",
                "status_code" : 404,
                "data": None,
                "error" : {
                    "status_code" : 404,
                    "status":"Error",
                    "message" : "only admin image can upload",
                }
            },
        )

    if file_collection == 'api':

        file_id = admin_profile.profile_image

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
        update_profile_info = crud.update_profile(db=db, user_id= admin_profile.users_id, update_data= update_data)
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

    