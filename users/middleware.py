import jwt
from django.utils.deprecation import MiddlewareMixin
from .models import User
from .utils import verify_access_token

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Проверяет JWT access-токен.
    Добавляет request.user, request.user_obj, request.user_jwt.
    """

    def process_request(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        request.user = None
        request.user_obj = None
        request.user_jwt = None

        if not auth_header or not auth_header.lower().startswith("bearer "):
            return

        token = auth_header.split(" ")[1].strip()
        try:
            payload = verify_access_token(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return  # не прерываем выполнение — пользователь просто анонимный

        user_id = payload.get("user_id")
        if not user_id:
            return

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return
import jwt
from django.utils.deprecation import MiddlewareMixin
from .models import User
from .utils import verify_access_token

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Проверяет JWT access-токен.
    Добавляет request.user, request.user_obj, request.user_jwt.
    """

    def process_request(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        request.user = None
        request.user_obj = None
        request.user_jwt = None

        if not auth_header or not auth_header.lower().startswith("bearer "):
            return

        token = auth_header.split(" ")[1].strip()
        try:
            payload = verify_access_token(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return  # не прерываем выполнение — пользователь просто анонимный

        user_id = payload.get("user_id")
        if not user_id:
            return

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return

        # ✅ Устанавливаем в DRF и в request
        request.user = user
        request.user_obj = user
        request.user_jwt = payload

        # ✅ Устанавливаем в DRF и в request
        request.user = user
        request.user_obj = user
        request.user_jwt = payload
