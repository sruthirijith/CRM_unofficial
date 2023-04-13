import re
import random
import array

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


def create_new_password():
    
    max_len = 10

    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    upper_char = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                        'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                        'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                        'Z']

    lower_char = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                        'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                        'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                        'z']

    symbols = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
            '*', '(', ')', '<']

    combined_list = digits + upper_char + lower_char + symbols

    rand_digit = random.choice(digits)
    rand_upper = random.choice(upper_char)
    rand_lower = random.choice(lower_char)
    rand_symbol = random.choice(symbols)

    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

    for x in range(max_len - 4):
        temp_pass = temp_pass + random.choice(combined_list)

        temp_pass_list = array.array('u', temp_pass)
        random.shuffle(temp_pass_list)
        
    password = ""
    for x in temp_pass_list:
            password = password + x

    return password


# print(get_hashed_password("C@le6ale"))


# is_pass = verify_password("C@le6ale", "$2b$12$i.d2uBy4y.ey1XkTM0kI5.nU//vNgpGgA8YhV980feGTk2nJP8bnu")
# print(is_pass)



