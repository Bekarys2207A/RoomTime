import jwt, uuid
from datetime import datetime, timezone
from django.conf import settings


def _now():
    """Возвращает текущее время в UTC."""
    return datetime.now(timezone.utc)



def make_access_token(user):
    """Создаёт короткоживущий JWT access token."""
    now = _now()
    exp = now + settings.JWT_ACCESS_TOKEN_LIFETIME
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token



def verify_access_token(token):
    """Проверяет JWT access token и возвращает payload."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Access token expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")



def make_refresh_token():
    """Создаёт случайный refresh token (строку)."""
    return uuid.uuid4().hex



def make_password_reset_token(user):
    """JWT-токен для восстановления пароля."""
    now = _now()
    exp = now + settings.JWT_RESET_TOKEN_LIFETIME
    payload = {
        "user_id": user.id,
        "action": "password_reset",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "nonce": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token
