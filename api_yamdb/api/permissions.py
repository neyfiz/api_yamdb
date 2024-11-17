from rest_framework.permissions import BasePermission
from rest_framework import permissions

from reviews.models import UserRole


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == UserRole.ADMIN

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return obj == request.user.role == UserRole.ADMIN


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


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Разрешаем только для методов GET, HEAD, OPTIONS (для чтения)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Запрещаем PUT и PATCH запросы для всех пользователей, кроме автора
        if request.method in ['PUT', 'PATCH']:
            return obj.author == request.user
        
        return False
