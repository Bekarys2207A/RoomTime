from rest_framework.permissions import BasePermission

class IsAuthenticatedJWT(BasePermission):
    """Проверяет, что пользователь аутентифицирован через JWT."""
    message = "Authentication credentials were not provided or are invalid."

    def has_permission(self, request, view):
        return getattr(request, "user_jwt", None) is not None


class IsAdmin(BasePermission):
    """Доступ только для администратора."""
    message = "Admin privileges required."

    def has_permission(self, request, view):
        role = getattr(request, "user_role", None)
        return role == "admin"


class IsAdminOrOwner(BasePermission):
    """
    Доступ для администратора или владельца объекта.
    Объект должен иметь поле `user`.
    """
    message = "Admin or owner privileges required."

    def has_object_permission(self, request, view, obj):
        user_id = getattr(request, "user_id", None)
        role = getattr(request, "user_role", None)
        if role == "admin":
            return True
        return hasattr(obj, "user") and getattr(obj.user, "id", None) == user_id