from rest_framework.permissions import BasePermission

class IsAuthenticatedJWT(BasePermission):
    """Проверяет, что пользователь аутентифицирован через JWT."""
    message = "Authentication credentials were not provided or are invalid."

    def has_permission(self, request, view):
        return getattr(request, "user_obj", None) is not None


class IsAdmin(BasePermission):
    """Доступ только для администратора."""
    message = "Admin privileges required."

    def has_permission(self, request, view):
        user = getattr(request, "user_obj", None)
        return user is not None and user.role == "admin"


class IsAdminOrOwner(BasePermission):
    """Админ или владелец объекта (например, своей брони)."""
    def has_object_permission(self, request, view, obj):
        user = getattr(request, "user_obj", None)
        return user and (user.role == "admin" or getattr(obj, "user", None) == user)
