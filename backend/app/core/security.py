import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError,
    InvalidSignatureError,
)
from datetime import datetime, timezone, timedelta
from pwdlib import PasswordHash
import redis

from app.core.config import settings
from app.schemas.uitls import HTTPError, error_codes

password_hash = PasswordHash.recommended()
redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return password_hash.hash(password)


def create_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@error_codes(400, 401)
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        if not payload.get("sub"):
            raise HTTPError(status_code=400, msg="Invalid token payload")
        return payload
    except ExpiredSignatureError:
        raise HTTPError(status_code=401, msg="This link has expired")
    except InvalidSignatureError:
        raise HTTPError(status_code=401, msg="Invalid token signature")
    except InvalidTokenError:
        raise HTTPError(status_code=401, msg="Invalid token")


def verify_token(token: str) -> str:
    payload = decode_token(token=token)
    return payload["sub"]


def is_token_already_used(token: str) -> bool:
    if redis_client.get(token):
        return True
    return False


def mark_token_as_used(token: str) -> None:
    payload = decode_token(token)

    expiry_timestamp = payload.get("exp")
    current_timestamp = datetime.now(timezone.utc).timestamp()
    ttl = int(expiry_timestamp - current_timestamp)

    if ttl > 0:
        redis_client.setex(token, ttl, "used")
