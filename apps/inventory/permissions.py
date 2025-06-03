from rest_framework.permissions import BasePermission

class IsAdminOrDistributor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['A1', 'A2']

class IsAgencyItselfOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == 'A3' and obj.agency == request.user.userprofile.agency
        ) or request.method in ['GET']
