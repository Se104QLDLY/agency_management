from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that extracts token from HttpOnly cookies
    per docs/api.md specifications
    """
    def authenticate(self, request):
        # Try Authorization header first
        header_auth = super().authenticate(request)
        if header_auth:
            return header_auth
            
        # Try HttpOnly cookie
        raw_token = request.COOKIES.get('access')
        if raw_token is None:
            return None
            
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        return (user, validated_token)
    
    def get_user(self, validated_token):
        """Get user from JWT token - Override for custom User model"""
        from .models import User
        try:
            user_id = validated_token.get('user_id')
            if user_id:
                return User.objects.select_related('account').get(user_id=user_id)
        except User.DoesNotExist:
            pass
        return None


class BaseScopePermission(permissions.BasePermission):
    """
    Base permission class for scope-based authorization per docs/api.md
    """
    required_scopes = []
    
    def has_permission(self, request, view):
        if not request.user or isinstance(request.user, AnonymousUser):
            return False
            
        if not request.user.account:
            return False
            
        user_role = request.user.account.account_role
        
        # Admin has access to everything
        if user_role == 'admin':
            return True
            
        # Check if user role has required scopes
        return self.check_user_scopes(user_role, request.method)
    
    def check_user_scopes(self, user_role, method):
        """Check if user role has required scopes for the HTTP method"""
        # Map HTTP methods to scope types
        scope_map = {
            'GET': 'read',
            'POST': 'write', 
            'PUT': 'write',
            'PATCH': 'write',
            'DELETE': 'write'
        }
        
        required_scope_type = scope_map.get(method, 'read')
        
        for scope in self.required_scopes:
            scope_parts = scope.split(':')
            if len(scope_parts) == 2 and scope_parts[1] == required_scope_type:
                return self.has_role_scope(user_role, scope)
                
        return False
    
    def has_role_scope(self, user_role, scope):
        """Check if user role has specific scope"""
        # Define role-based scope mappings per docs/api.md
        role_scopes = {
            'admin': [
                'user:read', 'user:write',
                'agency:read', 'agency:write', 
                'inventory:read', 'inventory:write',
                'finance:read', 'finance:write',
                'config:read', 'config:write',
                'report:read', 'profile:read', 'profile:write'
            ],
            'staff': [
                'agency:read', 'agency:write',
                'inventory:read', 'inventory:write', 
                'finance:read', 'finance:write',
                'report:read', 'profile:read', 'profile:write'
            ],
            'agent': [
                'agency:read', 'inventory:read',
                'profile:read', 'profile:write'
            ]
        }
        
        return scope in role_scopes.get(user_role, [])


class AgencyPermission(BaseScopePermission):
    """Permission for agency management endpoints"""
    required_scopes = ['agency:read', 'agency:write']


class InventoryPermission(BaseScopePermission):
    """Permission for inventory management endpoints"""  
    required_scopes = ['inventory:read', 'inventory:write']


class FinancePermission(BaseScopePermission):
    """Permission for finance management endpoints"""
    required_scopes = ['finance:read', 'finance:write']


class UserPermission(BaseScopePermission):
    """Permission for user management endpoints"""
    required_scopes = ['user:read', 'user:write']


class ConfigPermission(BaseScopePermission):
    """Permission for system configuration endpoints"""
    required_scopes = ['config:read', 'config:write']


class ProfilePermission(BaseScopePermission):
    """Permission for profile management endpoints"""
    required_scopes = ['profile:read', 'profile:write']


class ReportPermission(BaseScopePermission):
    """Permission for reporting endpoints"""
    required_scopes = ['report:read']


class PublicPermission(permissions.AllowAny):
    """Permission for public endpoints (login, register)"""
    pass 