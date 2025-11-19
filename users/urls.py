from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    RegisterView, LoginView, RefreshView, LogoutView,
    ForgotView, ResetView, MeView
)

# Swagger / OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="RoomTime Users API",
        default_version="v1",
        description=(
            "RoomTime — User Authentication Module (JWT-based).\n\n"
            "**Endpoints:**\n"
            "- `POST /register/` — Register a new user\n"
            "- `POST /login/` — Login and receive tokens\n"
            "- `POST /refresh/` — Refresh access and refresh tokens\n"
            "- `POST /logout/` — Logout and revoke refresh token\n"
            "- `POST /forgot/` — Request password reset email\n"
            "- `POST /reset/` — Set a new password using token\n"
            "- `GET /me/` — Get current authenticated user info\n\n"
            "**Authorization:**\n"
            "Use the **Authorize** button and provide `Bearer <access_token>` to authenticate."
        ),
        contact=openapi.Contact(email="support@roomtime.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Authentication Endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forgot/", ForgotView.as_view(), name="forgot"),
    path("reset/", ResetView.as_view(), name="reset"),
    path("me/", MeView.as_view(), name="me"),

    # API Documentation
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="users-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="users-redoc"),
]