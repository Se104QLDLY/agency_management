# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError


class AccountManager(models.Manager):
    def create_user(self, username, password_hash, account_role, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if account_role not in dict(Account.ACCOUNT_ROLE_CHOICES):
            raise ValueError("Invalid account_role")
        account = self.model(
            username=username,
            password_hash=password_hash,
            account_role=account_role,
            **extra_fields
        )
        account.save(using=self._db)
        return account

    def create_superuser(self, username, password_hash, **extra_fields):
        return self.create_user(
            username=username,
            password_hash=password_hash,
            account_role=Account.ADMIN,
            **extra_fields
        )


class Account(models.Model):
    ADMIN = 'admin'
    STAFF = 'staff'
    AGENT = 'agent'
    ACCOUNT_ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (STAFF, 'Staff'),
        (AGENT, 'Agent'),
    ]

    account_id = models.AutoField(primary_key=True, db_column="account_id")
    username = models.CharField(max_length=50, unique=True, db_column="username")
    password_hash = models.CharField(max_length=255, db_column="password_hash")
    account_role = models.CharField(max_length=20, choices=ACCOUNT_ROLE_CHOICES, db_column="account_role")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")
    updated_at = models.DateTimeField(null=True, blank=True, db_column="updated_at", auto_now=True)

    objects = AccountManager()

    class Meta:
        db_table = '"auth"."account"'
        ordering = ["username"]
        indexes = [
            models.Index(fields=["account_role"]),
        ]
        managed = False

    def __str__(self):
        return f"{self.username} ({self.account_role})"


class User(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_column="account_id", related_name="users")
    full_name = models.CharField(max_length=100, db_column="full_name")
    email = models.CharField(max_length=100, unique=True, null=True, blank=True, db_column="email")
    phone_number = models.CharField(max_length=15, null=True, blank=True, db_column="phone_number")
    address = models.CharField(max_length=255, null=True, blank=True, db_column="address")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")
    updated_at = models.DateTimeField(null=True, blank=True, db_column="updated_at", auto_now=True)

    objects = models.Manager()

    class Meta:
        db_table = '"auth"."user"'
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["account"]),
        ]
        managed = False

    def __str__(self):
        return self.full_name

    def clean(self):
        if self.account and self.account.account_role == Account.AGENT and not self.email:
            raise ValidationError({'email': "Agent user must have an email."})
        if self.phone_number:
            if not (self.phone_number.isdigit() and 10 <= len(self.phone_number) <= 15):
                raise ValidationError({'phone_number': "Phone number must be 10–15 digits."})

    def get_full_name(self):
        return self.full_name
