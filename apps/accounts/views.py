from rest_framework import viewsets
from .models import Account, Role, AccountRole, UserProfile
from .serializers import AccountSerializer, RoleSerializer, AccountRoleSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

class AccountRoleViewSet(viewsets.ModelViewSet):
    queryset = AccountRole.objects.all()
    serializer_class = AccountRoleSerializer
    permission_classes = [IsAdminUser]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]