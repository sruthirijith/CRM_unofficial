import re

from passlib.context import CryptContext
from config.base import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if settings.HASH_POLICY:
    password_context.load_path(settings.HASH_POLICY)


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


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



# print(get_hashed_password("C@le6ale"))


# is_pass = verify_password("C@le6ale", "$2b$12$i.d2uBy4y.ey1XkTM0kI5.nU//vNgpGgA8YhV980feGTk2nJP8bnu")
# print(is_pass)



