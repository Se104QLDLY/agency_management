from rest_framework.permissions import BasePermission

class IsDistributorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name__in=["A1", "A2"]).exists()
