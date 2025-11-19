import jwt, uuid
from datetime import datetime, timezone
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

def _now():
    return datetime.now(timezone.utc)


def make_access_token(user):
    token = AccessToken.for_user(user)
    return str(token)


def make_refresh_token():
    return uuid.uuid4().hex


def make_password_reset_token(user):
    now = _now()
    exp = now + settings.JWT_RESET_TOKEN_LIFETIME
    payload = {
        "user_id": user.id,
        "action": "password_reset",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "nonce": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.JWT_RESET_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def verify_reset_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_RESET_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("action") != "password_reset":
            return None
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None