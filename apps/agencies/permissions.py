from rest_framework import permissions

class IsAdminOrDistributor(permissions.BasePermission):
    """
    Cho phép nếu người dùng là quản trị viên hoặc nhà phân phối.
    Dùng cho các thao tác thêm/sửa/xóa đại lý.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_staff or
            request.user.groups.filter(name__in=["Quản trị viên", "Nhà phân phối"]).exists()
        )


class IsAdminOnly(permissions.BasePermission):
    """
    Chỉ quản trị viên mới có quyền thực hiện hành động.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="Quản trị viên").exists()


class IsDistributorOnly(permissions.BasePermission):
    """
    Chỉ nhà phân phối mới có quyền (ví dụ: xuất hàng).
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="Nhà phân phối").exists()


class IsAgencyItselfOrAdmin(permissions.BasePermission):
    """
    Chỉ cho phép đại lý tự thao tác với chính mình, hoặc quản trị viên.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
