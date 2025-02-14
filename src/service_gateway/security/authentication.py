import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from decouple import config
from jose import ExpiredSignatureError, JWTError, jwt

from src.utils.function_responses import ResponseComplete, ResponseMessage

# Environment variables
SECRET_KEY = str(config("SECRET_KEY"))
ALGORITHM = str(config("ALGORITHM"))
EXPIRATION_TIME_IN_MINUTES = int(config("EXPIRATION_TIME_IN_MINUTES"))

# Password hasher
ph = PasswordHasher()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=EXPIRATION_TIME_IN_MINUTES
        )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> ResponseComplete[Optional[Dict[str, Any]]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return ResponseComplete(msg="Authenticated", data=payload, ok=True)
    except ExpiredSignatureError:
        return ResponseComplete(msg="Expired Token", data=None, ok=False)
    except JWTError:
        return ResponseComplete(msg="Invalid Token", data=None, ok=False)


def validate_password(value: str) -> ResponseMessage:
    message: str = ""

    if len(value) < 8:
        message = "The password must be at least 8 characters long"
    if not re.search(r"[A-Z]", value):
        message = "The password must contain at least one uppercase letter"
    if not re.search(r"\d", value):
        message = "The password must contain at least one number"
    if not re.search(r"[@$!%_*?&-]", value):
        message = "The password must contain at least one special character (@$!%_*?&-)"

    if message:
        return ResponseMessage(msg=message, ok=False)

    return ResponseMessage(msg="Password is valid", ok=True)


def validate_password_match(password: str, confirm_password: str) -> ResponseMessage:
    if password != confirm_password:
        return ResponseMessage(msg="Password and re-password do not match", ok=False)
    return ResponseMessage(msg="Password and re-password match", ok=True)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        result = ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        result = False

    return result


def hash_password(password: str) -> str:
    return ph.hash(password)
