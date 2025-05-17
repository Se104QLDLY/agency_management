from rest_framework import serializers
from .models import Account, Role, AccountRole, UserProfile

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class AccountRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRole
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'roles', 'profile', 'created_at', 'updated_at']