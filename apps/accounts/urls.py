from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, UserProfileViewSet,
    LoginHistoryViewSet, RegisterAPIView, VerifyEmailAPIView
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'login-history', LoginHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
]
