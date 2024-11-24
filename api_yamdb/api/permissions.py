from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminAndAuthenticated(BasePermission):
    """Разрешение для администраторов и аутентифицированных пользователей."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminUserOnly(BasePermission):
    """Разрешение, доступное только администраторам."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
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

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
