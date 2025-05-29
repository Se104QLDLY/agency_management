from rest_framework import serializers
from .models import Account, UserProfile, LoginHistory


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'role', 'is_active', 'created_at', 'updated_at', 'profile']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = '__all__'
