from rest_framework.permissions import BasePermission

class IsAdminOnly(BasePermission):
    """
    Chỉ cho phép A1 truy cập và thao tác với các quy định
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == 'A1'
