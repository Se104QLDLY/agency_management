from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.CustomLoginView.as_view(), name='login'),
    path('auth/refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    
    # User profile endpoints
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # User management endpoints (admin)
    path('', include(router.urls)),
] 