from rest_framework.permissions import BasePermission

class IsAdminOrDistributor(BasePermission):
    """
    Cho phép người dùng có role là A1 (admin) hoặc A2 (distributor).
    Dùng cho các chức năng kho: nhập, xuất hàng, cập nhật tồn kho.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['A1', 'A2']
