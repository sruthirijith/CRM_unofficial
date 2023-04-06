from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.jwt.auth_handler import decode_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403,
                    detail = {
                        "status": "Error",
                        "status_code": 403,
                        "data": None,
                        "error": {
                            "status_code": 403,
                            "status": "Error",
                            "message": "Invalid authentication scheme."
                        }
                    }
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail = {
                        "status": "Error",
                        "status_code": 403,
                        "data": None,
                        "error": {
                            "status_code": 403,
                            "status": "Error",
                            "message": "Invalid token or expired token."
                        }
                   }
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403,
                detail = {
                    "status": "Error",
                    "status_code": 403,
                    "data": None,
                    "error": {
                        "status_code": 403,
                        "status": "Error",
                        "message": "Not authenticated"
                    }
                }
            )

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_token(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
