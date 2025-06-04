from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'A1'

class IsDistributor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'A2'

class IsAgency(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'A3'

class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'A1'
