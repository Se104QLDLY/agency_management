from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Account, User
import re


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with email/username + password"""
    email = serializers.EmailField(required=False)
    username = serializers.CharField(max_length=50, required=False)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')

        if not email and not username:
            raise serializers.ValidationError("Either email or username must be provided")

        # Find user by email or username
        if email:
            try:
                user = User.objects.select_related('account').get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        else:
            try:
                account = Account.objects.get(username=username)
                user = User.objects.select_related('account').get(account=account)
            except (Account.DoesNotExist, User.DoesNotExist):
                raise serializers.ValidationError("Invalid credentials")

        # Verify password
        if not check_password(password, user.account.password_hash):
            raise serializers.ValidationError("Invalid credentials")

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile info"""
    account_role = serializers.CharField(source='account.account_role', read_only=True)
    username = serializers.CharField(source='account.username', read_only=True)
    agency_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'phone_number', 'address', 
                 'account_role', 'username', 'agency_id', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at']

    def get_agency_id(self, obj):
        """
        Return the agency_id if the user is linked to an agency.
        This handles cases where the user might not be an agent (e.g., admin, staff).
        """
        from agency.models import Agency
        try:
            agency = Agency.objects.get(user_id=obj.user_id)
            return agency.agency_id
        except Agency.DoesNotExist:
            return None

    def validate_email(self, value):
        if value:
            try:
                validate_email(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Invalid email format")
            
            # Check uniqueness excluding current user
            if self.instance:
                if User.objects.exclude(user_id=self.instance.user_id).filter(email=value).exists():
                    raise serializers.ValidationError("Email already exists")
            else:
                if User.objects.filter(email=value).exists():
                    raise serializers.ValidationError("Email already exists")
        return value

    def validate_phone_number(self, value):
        if value:
            if not re.match(r'^\d{10,15}$', value):
                raise serializers.ValidationError("Phone number must be 10-15 digits")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        
        # Check old password
        request = self.context.get('request')
        if request and request.user:
            user = User.objects.select_related('account').get(user_id=request.user.user_id)
            if not check_password(attrs['old_password'], user.account.password_hash):
                raise serializers.ValidationError("Old password is incorrect")
        
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    account_role = serializers.ChoiceField(choices=Account.ACCOUNT_ROLE_CHOICES, default=Account.AGENT)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'full_name', 'email', 
                 'phone_number', 'address', 'account_role']

    def validate_username(self, value):
        if Account.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required")
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")  
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        # Remove confirm_password and account_role from user data
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        username = validated_data.pop('username')
        account_role = validated_data.pop('account_role', Account.AGENT)

        # Create Account first
        account = Account.objects.create(
            username=username,
            password_hash=make_password(password),
            account_role=account_role
        )

        # Create User
        user = User.objects.create(account=account, **validated_data)
        return user


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (admin view)"""
    account_role = serializers.CharField(source='account.account_role', read_only=True)
    username = serializers.CharField(source='account.username', read_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'email', 'phone_number', 
                 'account_role', 'username', 'created_at']
        read_only_fields = ['user_id', 'created_at']


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""
    class Meta:
        model = Account
        fields = ['account_id', 'username', 'account_role', 'created_at', 'updated_at']
        read_only_fields = ['account_id', 'created_at', 'updated_at'] 