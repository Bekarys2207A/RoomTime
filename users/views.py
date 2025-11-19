from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging

from .models import User, RefreshToken, PasswordResetToken
from .serializers import (
    RegisterSerializer, LoginSerializer, RefreshSerializer,
    LogoutSerializer, ForgotSerializer, ResetSerializer
)
from .utils import make_access_token, make_refresh_token, make_password_reset_token, verify_reset_token
from .permissions import IsAuthenticatedJWT
from .tasks import send_password_reset_email

logger = logging.getLogger(__name__)


error_responses = {
    400: openapi.Response("Bad Request"),
    401: openapi.Response("Unauthorized"),
    403: openapi.Response("Forbidden"),
}


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Register a New User",
        operation_description="Creates a new user account and returns a success message.",
        request_body=RegisterSerializer,
        responses={201: openapi.Response("Registration successful"), **error_responses}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Registration successful."}, status=201)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="User Login",
        operation_description="Authenticate a user using email and password. Returns access and refresh tokens along with user details.",
        request_body=LoginSerializer,
        responses={200: openapi.Response("Tokens returned"), **error_responses}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Failed login attempt for {email}")
            return Response({"detail": "Invalid credentials."}, status=401)

        if not user.check_password(password):
            logger.warning(f"Failed login attempt for {email}")
            return Response({"detail": "Invalid credentials."}, status=401)

        access = make_access_token(user)
        refresh = make_refresh_token()
        expires_at = timezone.now() + settings.JWT_REFRESH_TOKEN_LIFETIME
        RefreshToken.objects.create(user=user, token=refresh, expires_at=expires_at)

        return Response({
            "access_token": access,
            "refresh_token": refresh,
            "user": {"email": user.email, "role": user.role}
        })


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Refresh Tokens",
        operation_description="Rotates the refresh token and generates a new access token. The old refresh token becomes invalid.",
        request_body=RefreshSerializer,
        responses={200: openapi.Response("Access and refresh tokens rotated"), **error_responses}
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_token = serializer.validated_data["refresh_token"]

        with transaction.atomic():
            try:
                rtoken = RefreshToken.objects.select_for_update().get(token=old_token)
            except RefreshToken.DoesNotExist:
                logger.warning(f"Invalid refresh token used: {old_token}")
                return Response({"detail": "Invalid refresh token."}, status=401)

            if rtoken.revoked or rtoken.expires_at < timezone.now():
                logger.warning(f"Expired/revoked refresh token: {old_token}")
                return Response({"detail": "Token expired or revoked."}, status=401)

            # Rotate refresh token
            rtoken.revoked = True
            rtoken.save()
            new_refresh = make_refresh_token()
            RefreshToken.objects.create(user=rtoken.user, token=new_refresh,
                                        expires_at=timezone.now() + settings.JWT_REFRESH_TOKEN_LIFETIME)

        access = make_access_token(rtoken.user)
        return Response({"access_token": access, "refresh_token": new_refresh})


class LogoutView(APIView):
    permission_classes = [IsAuthenticatedJWT]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Logout User",
        operation_description="Revokes the provided refresh token and terminates the user's session.",
        request_body=LogoutSerializer,
        responses={200: openapi.Response("Logged out successfully"), **error_responses}
    )
    def post(self, request):
        token = request.data.get("refresh_token")
        if token:
            RefreshToken.objects.filter(token=token).update(revoked=True)
        return Response({"detail": "Logged out successfully."})


class ForgotView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Request Password Reset",
        operation_description="Sends a password reset link to the specified email address if the user exists.",
        request_body=ForgotSerializer,
        responses={200: openapi.Response("Password reset email sent"), **error_responses}
    )
    def post(self, request):
        serializer = ForgotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "If email exists, reset link sent."}, status=200)

        token = make_password_reset_token(user)
        link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        send_password_reset_email.delay(user.email, link)

        logger.info(f"Password reset requested for {email}")
        return Response({"detail": "If email exists, reset link sent."}, status=200)


class ResetView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Reset Password",
        operation_description="Resets the user's password using the provided token and sets a new password.",
        request_body=ResetSerializer,
        responses={200: openapi.Response("Password successfully reset"), **error_responses}
    )
    def post(self, request):
        serializer = ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        payload = verify_reset_token(token)
        if not payload:
            return Response({"detail": "Invalid or expired token."}, status=400)

        with transaction.atomic():
            user = get_object_or_404(User, id=payload["user_id"])
            prt, _ = PasswordResetToken.objects.get_or_create(
                token=token,
                defaults={"user": user, "expires_at": timezone.now() + settings.JWT_RESET_TOKEN_LIFETIME}
            )
            if prt.used:
                return Response({"detail": "Token already used."}, status=400)

            user.set_password(new_password)
            user.save()
            RefreshToken.objects.filter(user=user).update(revoked=True)
            prt.used = True
            prt.save()

        logger.info(f"Password successfully reset for {user.email}")
        return Response({"detail": "Password successfully reset."})


class MeView(APIView):
    permission_classes = [IsAuthenticatedJWT]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Get Current User",
        operation_description="Returns detailed information about the currently authenticated user.",
        responses={200: openapi.Response("Current user data"), **error_responses}
    )
    def get(self, request):
        if not request.user_id:
            return Response({"detail": "Unauthorized"}, status=401)
        return Response({
            "id": request.user_id,
            "role": request.user_role,
            "payload": request.user_jwt
        })