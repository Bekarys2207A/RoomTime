from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
import jwt

from .models import User, RefreshToken
from .serializers import (
    RegisterSerializer, LoginSerializer, RefreshSerializer,
    ForgotSerializer, ResetSerializer, LogoutSerializer
)
from .utils import make_access_token, make_refresh_token, make_password_reset_token
from .permissions import IsAuthenticatedJWT

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterView(APIView):
    """User Registration Endpoint"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Register a New User",
        operation_description="Creates a new user account and returns a success message.",
        request_body=RegisterSerializer,
        responses={201: openapi.Response('Registration successful')}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Registration successful."}, status=201)


class LoginView(APIView):
    """User Login Endpoint"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="User Login",
        operation_description="Authenticate a user using email and password. Returns access and refresh tokens along with user details.",
        request_body=LoginSerializer,
        responses={200: openapi.Response('Tokens returned')}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=401)

        if not user.check_password(password):
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
    """Token Refresh Endpoint"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Refresh Tokens",
        operation_description="Rotates the refresh token and generates a new access token. The old refresh token becomes invalid.",
        request_body=RefreshSerializer,
        responses={200: openapi.Response("Access and refresh tokens rotated")}
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_token = serializer.validated_data["refresh_token"]

        try:
            rtoken = RefreshToken.objects.get(token=old_token)
        except RefreshToken.DoesNotExist:
            return Response({"detail": "Invalid refresh token."}, status=401)

        if rtoken.revoked or rtoken.expires_at < timezone.now():
            return Response({"detail": "Token expired or revoked."}, status=401)

        rtoken.revoked = True
        rtoken.save()

        new_refresh = make_refresh_token()
        RefreshToken.objects.create(
            user=rtoken.user,
            token=new_refresh,
            expires_at=timezone.now() + settings.JWT_REFRESH_TOKEN_LIFETIME
        )

        access = make_access_token(rtoken.user)
        return Response({
            "access_token": access,
            "refresh_token": new_refresh
        })


class LogoutView(APIView):
    """User Logout Endpoint"""
    permission_classes = [IsAuthenticatedJWT]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Logout User",
        operation_description="Revokes the provided refresh token and terminates the user's session.",
        request_body=LogoutSerializer,
        responses={200: openapi.Response("Logged out successfully")}
    )
    def post(self, request):
        token = request.data.get("refresh_token")
        if token:
            RefreshToken.objects.filter(token=token).update(revoked=True)
        return Response({"detail": "Logged out successfully."}, status=200)


class ForgotView(APIView):
    """Password Reset Request Endpoint"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Request Password Reset",
        operation_description="Sends a password reset link to the specified email address if the user exists.",
        request_body=ForgotSerializer,
        responses={200: openapi.Response("Password reset email sent")}
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
        link = f"{request.scheme}://{request.get_host()}/api/users/reset?token={token}"

        send_mail(
            "RoomTime Password Reset",
            f"Click the link:\n{link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response({"detail": "If email exists, reset link sent."}, status=200)


class ResetView(APIView):
    """Password Reset Endpoint"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Reset Password",
        operation_description="Resets the user's password using the provided token and sets a new password.",
        request_body=ResetSerializer,
        responses={200: openapi.Response("Password successfully reset")}
    )
    def post(self, request):
        serializer = ResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("action") != "password_reset":
                return Response({"detail": "Invalid token."}, status=400)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token expired."}, status=400)
        except Exception:
            return Response({"detail": "Invalid token."}, status=400)

        user = get_object_or_404(User, id=payload["user_id"])
        user.set_password(new_password)
        user.save()

        RefreshToken.objects.filter(user=user).update(revoked=True)
        return Response({"detail": "Password successfully reset."})


class MeView(APIView):
    """Current User Info Endpoint"""
    permission_classes = [IsAuthenticatedJWT]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Get Current User",
        operation_description="Returns detailed information about the currently authenticated user.",
        responses={200: openapi.Response("Current user data")}
    )
    def get(self, request):
        user = request.user_obj
        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at,
        })