from sqlalchemy.orm import Session, load_only
from passlib.context import CryptContext
from sqlalchemy import and_ 
from fastapi import HTTPException
import gridfs

from bson.objectid import ObjectId
from core.jwt import auth_handler
from core.api.sales_person.models import Users, UserRoles
from core.api.sales_person.crud import (
    generate_referralcode,
    get_user_by_email,
    check_role )
from core.api.admin import models
from core.api.super_admin import schema
from core.utils import password, time


def create_user(db: Session, user: schema.AdminCreate):
    hashed_password = password.get_hashed_password(password = user.password)
    db_user = Users(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number,
        created_at=time.utc_time(),
        updated_at=time.utc_time(),
        referral_code=generate_referralcode(int(user.phone_number[-10:])),
    )
    db.add(db_user)
    db.flush()
    
    role = UserRoles(
        users_id=db_user.id,
        role_id=user.role_id
    )
    print(user.dob)
    db.add(role)
    db_admin = models.AdminProfile(
        users_id = db_user.id,
        dob = user.dob,
        gender = user.gender,
        last_login = time.utc_time()
    )
    db.add(db_admin)
    db.commit()
    return db_user, role, db_admin

def check_admin_exist(db : Session, users_id : int):
    return db.query(models.AdminProfile).filter(models.AdminProfile.users_id == users_id).first()

def create_admin_profile(db : Session, users : schema.AdminCreate):
    db_create = models.AdminProfile(
        users_id = users.users_id,
        dob = users.dob,
        gender = users.gender,
        last_login = users.last_login,
        profile_image = users.profile_image
    )
    db.add(db_create)
    db.commit()
    db.refresh(db_create)
    return db_create

def update_admin_profile(db : Session, users_id : int, profile : dict):
    if "full_name" in profile:
        result = db.query(Users).filter(Users.id == users_id).update({"full_name":profile["full_name"]})
        db.commit()
        del profile["full_name"]
    result = db.query(models.AdminProfile).filter(models.AdminProfile.users_id == users_id).update(profile)
    db.commit()
    return result

def update_block_user(db : Session, users_id : int, block : bool):
    result = db.query(Users).filter(Users.id == users_id).update({"blocked" : block})
    db.commit()
    return result

def get_users_id_from_roles(db : Session):
    return db.query(UserRoles.users_id).filter(UserRoles.role_id == 2).all()

def display_blocked_admin(db : Session, users_id : list):
    profile_data = db.query(models.AdminProfile.id.label("admin_id"),
                             Users.id.label("user_id"), 
                             Users.full_name, 
                             Users.email, 
                             Users.phone_number,
                             Users.blocked)\
                            .join(Users,Users.id == models.AdminProfile.users_id, isouter=True)\
                            .filter( and_(Users.blocked == True, Users.id .in_(users_id))).all()
    return profile_data

def display_all_admin_profile(db : Session):
    profile_data = db.query(models.AdminProfile.id.label("admin_id"),
                            Users.id.label("user_id"),
                            Users.full_name,
                            Users.email,
                            Users.phone_number,
                            models.AdminProfile.dob,
                            models.AdminProfile.gender,
                            models.AdminProfile.last_login,
                            models.AdminProfile.profile_image,
                            Users.blocked)\
                            .join(Users,Users.id == models.AdminProfile.users_id, isouter=True).order_by(Users.id) .all()
    return profile_data

def check_super_admin(db,token):
    payload = auth_handler.decode_token(token=token)
    users = get_user_by_email(db, payload['sub'])
    if not users:
        raise HTTPException(
            status_code=404,
            detail={
                "status" : "Error",
                "status_code" : 404,
                "data" : None,
                "error" : {
                    "status_code":404,
                    "status":'Error', 
                    "message" : "Super admin not found."
                }
            }
        )
    role = check_role(db = db, users_id = users.id)
    if not role.__dict__['role_id'] in [1] :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Only super admin can access"
                }
            }
        )
    
def display_admin_profile(db : Session, users_id : int):
    profile_data = db.query(models.AdminProfile.id.label("admin_id"),
                            Users.id.label("user_id"),
                            Users.full_name,
                            Users.email,
                            Users.phone_number,
                            models.AdminProfile.dob,
                            models.AdminProfile.gender,
                            models.AdminProfile.last_login,
                            models.AdminProfile.profile_image,
                            Users.blocked)\
                            .join(Users,Users.id == models.AdminProfile.users_id).filter(Users.id == users_id) .order_by(Users.id) .first()
    return profile_data

def check_admin_by_admin_id(db : Session, admin_id : int):
    return db.query(models.AdminProfile).filter(models.AdminProfile.id == admin_id).first()

def update_profile(db : Session, user_id : int, update_data : dict):
    result = db.query(models.AdminProfile).filter(models.AdminProfile.users_id==user_id).update(update_data)
    db.commit()
    return result

def update_admin_profile(db : Session, user_id : int, update_data : dict):
    if "full_name" in update_data:
        result = db.query(Users).filter(Users.id == user_id).update({"full_name":update_data["full_name"]})
        db.commit()
        del update_data["full_name"]
    result = db.query(models.AdminProfile).filter(models.AdminProfile.users_id==user_id).update(update_data)
    db.commit()
    #db.refresh(result) 
    return result

def save_file(mongo_db , collection : str, file_name: str, content : bytes, content_type : str):
    try:
        fs = gridfs.GridFS(mongo_db, collection)
        stored = fs.put(content, filename=file_name, contentType=content_type)
        return stored
    except Exception as e:
        print(e)
        return False
    
def check_if_file_exists(mongo_db, collection : str, file_id : str):
    try:
        fs = gridfs.GridFS(mongo_db, collection)
        exists = fs.exists(ObjectId(file_id))
        if not exists:
            return False
        return True
    except Exception as e:
        print(e)

def retrieve_file(mongo_db, collection : str, file_id : str):
    try:
        fs = gridfs.GridFS(mongo_db, collection)
        result = fs.get(ObjectId(file_id)).read()
        return result
    except Exception as e:
        print(e)
        return False

def delete_file(mongo_db, collection : str, file_id : str):
    try:
        fs = gridfs.GridFS(mongo_db, collection)
        fs.delete(ObjectId(file_id))
        return True
    except Exception as e:
        print(e)
        return False
    
def create_superadmin(db : Session, user : schema.SuperAdmin) :
    hashed_password = password.get_hashed_password(password = user.password)
    db_create = Users(
        full_name = user.full_name,
        email = user.email,
        password = hashed_password,
        phone_number = user.phone_number,
        referral_code = user.referral_code
    )
    db.add(db_create)
    db.flush()
    role = UserRoles(
        users_id=db_create.id,
        role_id=user.role_id
    )
    db.add(role)
    db.commit()
    return True

def check_admin_exist(db : Session, admin_id):
    return db.query(models.AdminProfile).filter(models.AdminProfile.id == admin_id).first()