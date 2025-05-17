from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, RoleViewSet, AccountRoleViewSet, UserProfileViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'account-roles', AccountRoleViewSet)
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
