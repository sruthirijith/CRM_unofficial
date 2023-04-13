import phonenumbers

from fastapi.security import OAuth2PasswordBearer

import datetime
from hashids import Hashids
from sqlalchemy import and_
from sqlalchemy.orm import Session, load_only
from passlib.context import CryptContext

from core.utils import sendgrid_service
from config.base import settings
from core.api.sales_person import models
from core.api.admin.models import AdminProfile
from core.api.admin import schema
from core.database.connection import get_db
from core.utils import password, time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user_email_login")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM


def generate_referralcode(hash_input):
    hash_salt = settings.REFERRAL_CODE_HASH_SALT
    hashids = Hashids(salt=hash_salt, min_length=6)
    hash_output = hashids.encode(hash_input)
    return hash_output

def create_user(db: Session, user: schema.UserCreate):
    create_password = password.create_new_password()
    sendgrid_service.send_email(user.email, title = 'New Password', subject = 'New Password', action = None, message1 = 'New Password', message2 = create_password, action_url = None, support_url = settings.SENDGRID_EMAIL)
    hashed_password = password.get_hashed_password(password=create_password)
    db_user = models.Users(
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
    
    role = models.UserRoles(
        users_id=db_user.id,
        role_id=user.role_id
    )
    db.add(role)
    db.commit()
    return db_user, role


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).options(load_only(
            "id", "full_name", "email", "phone_number", "referral_code", "referred_by", "blocked", 
            "deleted", "created_at", "updated_at"
        )).filter(models.Users.email == email).first()

def get_user_by_phonenumber(db: Session, phone_number: str):
    return db.query(models.Users).options(load_only(
            "id", "full_name", "email", "phone_number", "referral_code", "referred_by", "blocked", 
            "deleted", "created_at", "updated_at"
        )).filter(models.Users.phone_number == phone_number).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.Users).options(load_only(
            "id", "full_name", "email", "phone_number", "referral_code", "referred_by", "blocked", 
            "deleted", "created_at", "updated_at"
        )).filter(models.Users.id == user_id).first()


def validate_phone_number(phone_number: str, country_code: str) -> bool:
    try:
        if country_code:
            phone_number_obj = phonenumbers.parse(phone_number, country_code)
        else:
            phone_number_obj = phonenumbers.parse(phone_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    if not phonenumbers.is_valid_number(phone_number_obj):
        return False
    return True

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def verify_email_password(db:Session , email:str ,password:str):
    userinfo = db.query(models.Users).filter(models.Users.email==email).first()
    verify_pass=verify_password(password,userinfo.password)

    if  verify_pass:
        return userinfo
        
    else:
        return None

def get_user_roles(db : Session, users_id : int, role : int):
    return db.query(models.UserRoles).filter(and_(models.UserRoles.users_id==users_id , models.UserRoles.role_id==role)).first()

def check_if_user_exists(db : Session, email : str):
    return get_user_by_email(db, email)

def check_role(db : Session, users_id : int):
    return db.query(models.UserRoles).filter(models.UserRoles.users_id == users_id).first()

def update_last_login(db : Session, users_id : int):
    update_admin = db.query(AdminProfile).update({"last_login" : datetime.datetime.now()})
    db.commit()
    return update_admin

def display_all_merchant_stages(db:Session):
    merchant_stages = db.query(models.MerchantStages).all()
    return merchant_stages


def start_time_tracking(db:Session,user_id:int):
    current_data = datetime.datetime.now()
    tracking_data = models.SalesPersonTimeTracking(
        users_id = user_id,
        date = datetime.datetime.today(),
        log_in_time = current_data.time(),
        active = "true"
    )

    db.add(tracking_data)
    db.commit()
    return tracking_data

def end_time_tracking(db:Session,user_id:int):


    get_data = db.query(models.SalesPersonTimeTracking).filter(models.SalesPersonTimeTracking.users_id==user_id,models.SalesPersonTimeTracking.active == "true").first()
    if get_data:
        current_data = datetime.datetime.now().time()
        time1 = datetime.datetime.strptime(str(get_data.log_in_time), "%H:%M:%S.%f")
        time2 = datetime.datetime.strptime(str(current_data), "%H:%M:%S.%f")
        delta = time2 - time1
        active_time = str(datetime.timedelta(seconds=delta.total_seconds()))

        get_data = db.query(models.SalesPersonTimeTracking).filter(models.SalesPersonTimeTracking.users_id == user_id,
                    models.SalesPersonTimeTracking.active == "true").update({'log_out_time':current_data,"active":"false","active_login_time":active_time})

        db.commit()
        return get_data
    else:
        return False
    

def list_time_logs_for_salesperson(db:Session,user_id:int):
    get_data = db.query(models.SalesPersonTimeTracking).filter(models.SalesPersonTimeTracking.users_id==user_id).all()
    return get_data

def get_sales_person_team_members(db : Session, users_id : int):
    return db.query(models.Users.id,
                    models.Users.email,
                    models.Users.full_name,
                    models.Users.phone_number,
                    models.SalesPersonProfile.designation,
                    models.SalesPersonProfile.profile_image
                    ).join(models.SalesPersonProfile, models.Users.id == models.SalesPersonProfile.users_id,
                    ).filter(models.Users.id != users_id).all()