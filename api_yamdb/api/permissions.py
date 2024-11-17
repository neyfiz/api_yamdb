from rest_framework.permissions import BasePermission

from reviews.models import UserRole


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.is_authenticated and (request.user.is_staff or
                                                  request.user.is_superuser or
                                                  request.user.role == UserRole.ADMIN)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return self.has_permission(request, view)


# тут еще переписать для себя и модератора
class IsSelfOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj == request.user or request.user.role == UserRole.ADMIN


class IsAdminOrModerator(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [UserRole.ADMIN, UserRole.MODERATOR]
