from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'A1'

class IsDistributor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'A2'

class IsAgency(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'A3'

class CanViewInventory(BasePermission):
    """
    A1, A2 xem được thống kê hàng hóa
    """
    def has_permission(self, request, view):
        return request.user.role in ['A1', 'A2']

class CanManageReceipt(BasePermission):
    """
    A2, A3 có thể nhập hàng
    """
    def has_permission(self, request, view):
        return request.user.role in ['A2', 'A3']

class CanManageIssue(BasePermission):
    """
    A2 mới có thể xuất hàng
    """
    def has_permission(self, request, view):
        return request.user.role == 'A2'
