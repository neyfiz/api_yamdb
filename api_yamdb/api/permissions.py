from rest_framework.permissions import SAFE_METHODS, BasePermission
from reviews.models import UserRole


class IsAdminOrAuthenticated(BasePermission):
    """Разрешение для администраторов и аутентифицированных пользователей."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.role == UserRole.ADMIN
        )


class IsAdminOnly(BasePermission):
    """Разрешение, доступное только администраторам."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == UserRole.ADMIN
        )


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение для автора объекта или только для чтения."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    """Разрешение для админа, модератора, автора или только для чтения."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.role in [UserRole.ADMIN, UserRole.MODERATOR]
            or obj.author == request.user
        )
