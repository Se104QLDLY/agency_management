from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'A1'

class IsDistributor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'A2'

class IsAdminOrDistributor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['A1', 'A2']
