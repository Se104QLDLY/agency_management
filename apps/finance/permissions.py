from rest_framework.permissions import BasePermission

class IsDistributorOrAgency(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['A2', 'A3']

class IsAllRoles(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['A1', 'A2', 'A3']
