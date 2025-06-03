from rest_framework.permissions import BasePermission

class IsAdminOrDistributor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['A1', 'A2']

class IsAllRoles(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['A1', 'A2', 'A3']
