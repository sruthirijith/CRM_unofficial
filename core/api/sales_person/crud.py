import phonenumbers
import re
from datetime import datetime, date, timedelta

from sqlalchemy.orm import Session
from core.api.sales_person import models, schema


def check_email(db:Session, email:str):
    return db.query(models.BDE).filter(models.BDE.email==email).first()

def check_phone(db:Session, phone_number:int):
    return db.query(models.BDE).filter(models.BDE.phone_number==phone_number).first()


def verify_email_password(db:Session , email:str ,password:str):
    return db.query(models.BDE).filter(models.BDE.email==email, models.BDE.password==password).first()

def create_user(db:Session, data:schema.registration):
    db_user = models.BDE(
            full_name = data.full_name,
            email     = data.email, 
            password  = data.password,  
            phone_number = data.phone_number
    )
    db.add(db_user)
    db.commit()
    

    return db_user


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

def validate_password(password: str) -> bool:
    """
    Has minimum 8 characters in length. Adjust it by modifying {8,}
    At least one uppercase English letter. You can remove this condition by removing (?=.*?[A-Z])
    At least one lowercase English letter.  You can remove this condition by removing (?=.*?[a-z])
    At least one digit. You can remove this condition by removing (?=.*?[0-9])
    At least one special character,  You can remove this condition by removing (?=.*?[#?!@$%^&*-])
    """
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    return True if re.match(password_pattern, password) else False

def get_user_by_email(db: Session, email: str):
    return db.query(models.BDE).filter(models.BDE.email == email).first()

def track_login(db:Session, users_id:int):
    db_login=models.track_time(
    users_id         = users_id,
    date            =date.today(),
    login_time = datetime.now() - timedelta(hours=0, minutes=30),
    active           =True
    )
    db.add(db_login)
    db.commit()
    return db_login



def get_duration(db:Session, users_id:int, hours:int, minutes:int):
    get_id = db.query(models.track_time).filter(models.track_time.users_id==users_id).first()
    login_time = get_id.__dict__['login_time'] 
    temp_logout_time = datetime.now()
    active_period_temp = temp_logout_time - login_time
    
    a = timedelta(hours=hours, minutes=minutes)
    if active_period_temp > a :
        logout_time =temp_logout_time
        db.query(models.track_time).filter(models.track_time.users_id==users_id).update({"logout_time":logout_time})
       
    hour =temp_logout_time.hour
    if hour >= 18 :
        logout_time_final = temp_logout_time + timedelta(hours=2, minutes=0)
        active_period_final = logout_time_final - login_time
        active_period = active_period_final - timedelta(hours=1)
        db.query(models.track_time).filter(models.track_time.users_id==users_id).update({"active_period":active_period, "logout_time":logout_time_final})
        db.commit()
        return True 
        
    
    

