import datetime

from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt,JWTError
from typing import Dict

from config.base import settings

secret = settings.JWT_SECRET_KEY
day = settings.JWT_TOKEN_EXPIRY_DAYS
algorithm = settings.ALGORITHM

def token_response(token: str):
    return {
        "access_token": token
    }

def encode_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=day, minutes=0),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    token = jwt.encode(
        payload,
        secret ,
        algorithm
    )
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, secret, algorithm)
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

def refresh_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=365, minutes=0),
        'iat': datetime.utcnow(),
        'scope' : 'refresh_token',
        'sub': user_id
    }
    return jwt.encode(
        payload,
        secret ,
        algorithm
    )

def refresh_access_token(refresh_token):
    try:
        payload = jwt.decode(refresh_token, secret, algorithm)

        if (payload['scope'] == 'refresh_token'):
            user_id = payload['sub']
            new_token = encode_token(user_id=user_id)
            return token_response(new_token)

        raise HTTPException(status_code=401, detail='Invalid scope for token')

    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

