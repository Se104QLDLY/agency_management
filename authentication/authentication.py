from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import User


class CookieJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that reads from HttpOnly cookies"""
    
    def get_raw_token(self, request):
        """Get JWT token from cookie or Authorization header"""
        # Try to get token from cookie first
        raw_token = request.COOKIES.get('access')
        if raw_token:
            return raw_token.encode('utf-8')
        
        # Fallback to Authorization header
        return super().get_raw_token(request)

    def get_user(self, validated_token):
        """Get user from JWT token"""
        try:
            user_id = validated_token.get('user_id')
            if user_id:
                return User.objects.select_related('account').get(user_id=user_id)
        except User.DoesNotExist:
            pass
        return None 