from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class AccountManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(username, password, **extra_fields)

class Account(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    roles = models.ManyToManyField(Role, through='AccountRole')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = AccountManager()

    def __str__(self):
        return self.username

class AccountRole(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LoginHistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)
    device = models.CharField(max_length=100)
    login_time = models.DateTimeField(auto_now_add=True)