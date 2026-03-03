from django.contrib import admin
from .models import User, RefreshToken, PasswordResetToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "role", "is_active", "created_at")
    search_fields = ("email", "username")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    ordering = ("-created_at",)


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "revoked")
    search_fields = ("token", "user__email")
    list_filter = ("revoked",)
    ordering = ("-expires_at",)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "used", "created_at", "expires_at")
    search_fields = ("token", "user__email")
    list_filter = ("used",)
    ordering = ("-created_at",)