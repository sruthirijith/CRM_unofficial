import gridfs

from bson.objectid import ObjectId
from sqlalchemy.orm import Session, load_only
from sqlalchemy import and_ 
from fastapi import HTTPException

from core.api.admin import schema
from core.api.sales_person import models
from core.jwt import auth_handler
from core.api.sales_person.models import Users, SalesPersonProfile, UserRoles
from core.api.sales_person.crud import (
    get_user_by_email,
    check_role )
from core.utils import password
from core.utils import sendgrid_service
from config.base import settings



def update_block_user(db : Session, users_id : int, block : bool):
    result = db.query(Users).filter(Users.id == users_id).update({"blocked" : block})
    db.commit()
    return result

def get_users_id_from_roles(db : Session):
    return db.query(UserRoles.users_id).filter(UserRoles.role_id == 6).all()

def display_blocked_sales_person(db : Session, users_id : list):
    profile_data = db.query(SalesPersonProfile.id,
                            Users.id.label("user_id"),
                            Users.full_name,
                            Users.email,
                            Users.phone_number,
                            Users.blocked)\
                            .join(Users,Users.id == SalesPersonProfile.users_id, isouter=True)\
                            .filter( and_(Users.blocked == True, Users.id .in_(users_id))).all()
    return profile_data

def check_admin(db, token):
    payload = auth_handler.decode_token(token=token)
    user = get_user_by_email(db, payload['sub'])
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
                    "message" : "User not found."
                }
            }
        )
    role = check_role(db = db, users_id = user.id)
    if not role.__dict__['role_id'] in [1,2] :
        raise HTTPException(
            status_code=400,
            detail={
                "status" : "Error",
                "status_code" : 400,
                "data" : None,
                "error" : {
                    "status_code":400,
                    "status":'Error', 
                    "message" : "Only super admin and admin can access"
                }
            }
        )
    
def get_user_by_id(db: Session, user_id: int):
    return db.query(Users).options(load_only(
            "id", "full_name", "email", "phone_number", "referral_code", "referred_by", "blocked", 
            "deleted", "created_at", "updated_at"
        )).filter(Users.id == user_id).first()

def get_sales_person(db : Session, users_id : int):
    return db.query(SalesPersonProfile).filter(SalesPersonProfile.users_id == users_id).first()

def create_sales_person(db : Session, users_id : int, sales_person : schema.CreateSalesPerson):
    add_db = SalesPersonProfile(
        users_id = users_id,
        dob = sales_person.dob,
        gender = sales_person.gender,
        address1 = sales_person.address1,
        address2 = sales_person.address2,
        city = sales_person.city,
        district = sales_person.district,
        state = sales_person.state,
        country = sales_person.country,
        postal_code = sales_person.postal_code,
        designation = sales_person.designation
    )
    db.add(add_db)
    db.commit()
    db.refresh(add_db)
    return add_db

def get_user_sales_person(db : Session):
    return db.query(UserRoles.users_id).filter(UserRoles.role_id == 6).all()

def display_all_sales_person(db : Session, users_id : list):
    profile_data = db.query(SalesPersonProfile.users_id,
                            Users.full_name,
                            Users.email,
                            Users.phone_number,
                            SalesPersonProfile.id,
                            SalesPersonProfile.dob,
                            SalesPersonProfile.gender,
                            SalesPersonProfile.address1,
                            SalesPersonProfile.address2,
                            SalesPersonProfile.city,
                            SalesPersonProfile.district,
                            SalesPersonProfile.state,
                            SalesPersonProfile.country,
                            SalesPersonProfile.postal_code,
                            SalesPersonProfile.profile_image,
                            SalesPersonProfile.created_at,
                            SalesPersonProfile.updated_at,
                            SalesPersonProfile.designation,
                            Users.blocked)\
                            .join(Users, Users.id == SalesPersonProfile.users_id, isouter=True)\
                            .filter(Users.id .in_(users_id)).order_by(SalesPersonProfile.id) .all()
    return profile_data

def get_sales_person_id(db : Session, sales_person_id : int):
    return db.query(SalesPersonProfile).filter(SalesPersonProfile.id == sales_person_id).first()

def update_sales_person(db : Session, sales_person_id : int, sales_person : dict, users_id : int ):
    if "full_name" in sales_person:
        result = db.query(Users).filter(Users.id == users_id).update({"full_name":sales_person['full_name']})
        db.commit()
        del sales_person['full_name']
    if sales_person :
        result = db.query(SalesPersonProfile).filter(SalesPersonProfile.id == sales_person_id).update(sales_person)
        db.commit()
        return result
    else :
        return True
    
def update_password(db : Session, users_id : int, email : str):
    create_password = password.create_new_password()
    sendgrid_service.send_email(email, title = 'Change Password', subject = 'Change Password', action = None, message1 = 'Change Password', message2 = create_password, action_url = None, support_url = settings.SENDGRID_EMAIL)
    hashed_password = password.get_hashed_password(password=create_password)
    password_update = db.query(Users).filter(Users.id == users_id).update({"password":hashed_password})
    db.commit()
    return password_update

def display_sales_person(db: Session, sales_person_id : int):
    profile_data = db.query(SalesPersonProfile.users_id,
                            Users.full_name,
                            Users.email,
                            Users.phone_number,
                            SalesPersonProfile.id,
                            SalesPersonProfile.dob,
                            SalesPersonProfile.gender,
                            SalesPersonProfile.address1,
                            SalesPersonProfile.address2,
                            SalesPersonProfile.city,
                            SalesPersonProfile.district,
                            SalesPersonProfile.state,
                            SalesPersonProfile.country,
                            SalesPersonProfile.postal_code,
                            SalesPersonProfile.profile_image,
                            SalesPersonProfile.created_at,
                            SalesPersonProfile.updated_at,
                            SalesPersonProfile.designation,
                            Users.blocked)\
                            .join(Users, Users.id == SalesPersonProfile.users_id, isouter=True)\
                            .filter(SalesPersonProfile.id == sales_person_id).first()
    return profile_data

def update_profile(db : Session, user_id : int, update_data : dict):
    result = db.query(SalesPersonProfile).filter(SalesPersonProfile.users_id==user_id).update(update_data)
    db.commit()
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
    

def list_time_logs(db:Session):
    get_data = db.query(models.SalesPersonTimeTracking).all()
    return get_data