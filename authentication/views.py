from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.conf import settings

from .models import Account, User
from .serializers import (
    LoginSerializer, UserProfileSerializer, ChangePasswordSerializer,
    UserRegistrationSerializer, UserListSerializer, AccountSerializer
)
from .permissions import CookieJWTAuthentication, UserPermission, ProfilePermission, PublicPermission


@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(APIView):
    """Custom login view that supports both email and username login"""
    permission_classes = [PublicPermission]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens - Fix for custom user model
            try:
                refresh = RefreshToken()
                refresh['user_id'] = user.user_id  # Use custom user_id field
                access_token = refresh.access_token
                access_token['user_id'] = user.user_id
                
                # Set HttpOnly cookies
                response = Response({
                    'user': {
                        'id': user.user_id,
                        'username': user.account.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'account_role': user.account.account_role
                    }
                }, status=status.HTTP_200_OK)
                
                # Set HttpOnly cookies for tokens
                response.set_cookie(
                    'access',
                    str(access_token),
                    max_age=60 * 60 * 24,  # 1 day
                    httponly=True,
                    secure=settings.AUTH_COOKIE_SECURE,
                    samesite=settings.AUTH_COOKIE_SAMESITE
                )
                response.set_cookie(
                    'refresh',
                    str(refresh),
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    httponly=True,
                    secure=settings.AUTH_COOKIE_SECURE,
                    samesite=settings.AUTH_COOKIE_SAMESITE
                )
                
                return response
            except Exception as e:
                return Response({'error': f'Token generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenRefreshView(APIView):
    """Custom token refresh view that works with HttpOnly cookies"""
    permission_classes = [PublicPermission]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            
            response = Response({'success': True}, status=status.HTTP_200_OK)
            response.set_cookie(
                'access',
                str(access_token),
                max_age=60 * 60 * 24,  # 1 day
                httponly=True,
                secure=settings.AUTH_COOKIE_SECURE,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            return response
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """Logout view that blacklists refresh token and clears cookies"""
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [ProfilePermission]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        
        response = Response({'success': True}, status=status.HTTP_200_OK)
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get and update current user profile"""
    serializer_class = UserProfileSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [ProfilePermission]

    def get_object(self):
        try:
            user = self.request.user
            print(f"DEBUG: request.user = {user}")
            print(f"DEBUG: type(request.user) = {type(user)}")
            print(f"DEBUG: hasattr user_id = {hasattr(user, 'user_id')}")
            if hasattr(user, 'user_id'):
                print(f"DEBUG: user.user_id = {user.user_id}")
                return User.objects.select_related('account').get(user_id=user.user_id)
            else:
                print(f"DEBUG: user attributes = {dir(user)}")
                raise Exception(f"User object has no user_id attribute: {type(user)}")
        except Exception as e:
            print(f"DEBUG ERROR: {str(e)}")
            raise


class ChangePasswordView(APIView):
    """Change user password"""
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [ProfilePermission]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = User.objects.select_related('account').get(user_id=request.user.user_id)
            user.account.password_hash = make_password(serializer.validated_data['new_password'])
            user.account.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [PublicPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Auto-login after registration - Fix for custom user model
            try:
                refresh = RefreshToken()
                refresh['user_id'] = user.user_id  # Use custom user_id field
                access_token = refresh.access_token
                access_token['user_id'] = user.user_id
                
                response = Response({
                    'user': {
                        'id': user.user_id,
                        'username': user.account.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'account_role': user.account.account_role
                    }
                }, status=status.HTTP_201_CREATED)
                
                # Set HttpOnly cookies
                response.set_cookie(
                    'access',
                    str(access_token),
                    max_age=60 * 60 * 24,  # 1 day
                    httponly=True,
                    secure=settings.AUTH_COOKIE_SECURE,
                    samesite=settings.AUTH_COOKIE_SAMESITE
                )
                response.set_cookie(
                    'refresh',
                    str(refresh),
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    httponly=True,
                    secure=settings.AUTH_COOKIE_SECURE,
                    samesite=settings.AUTH_COOKIE_SAMESITE
                )
                
                return response
            except Exception as e:
                return Response({'error': f'Token generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    """ViewSet for managing users (admin only)"""
    queryset = User.objects.select_related('account').all()
    permission_classes = []  # Will be set by get_permissions()
    authentication_classes = []  # Will be set by get_authenticators()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['account__account_role']
    search_fields = ['full_name', 'email', 'account__username']
    ordering_fields = ['created_at', 'full_name', 'account__username']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer

    def get_authenticators(self):
        """Return list of authentication classes"""
        return [CookieJWTAuthentication()]
    
    def get_permissions(self):
        """Admin required for user management"""
        return [UserPermission()]

    def perform_create(self, serializer):
        # Only admin can create users with specific roles
        request_user = User.objects.select_related('account').get(user_id=self.request.user.user_id)
        if request_user.account.account_role != Account.ADMIN:
            serializer.validated_data['account_role'] = Account.AGENT
        serializer.save()


# Utility functions


# Utility function to create JWT for user
def create_jwt_for_user(user):
    """Helper function to create JWT tokens for a user"""
    refresh = RefreshToken()
    refresh['user_id'] = user.user_id  # Use custom user_id field
    access_token = refresh.access_token
    access_token['user_id'] = user.user_id
    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }
