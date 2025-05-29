from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Chỉ cho phép người dùng có role là 'A1' (quản trị viên) thao tác.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'A1'
