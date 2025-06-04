from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile, LoginHistory

class AccountAdmin(UserAdmin):
    model = Account
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'full_name', 'phone', 'address', 'created_at', 'updated_at')
    search_fields = ('full_name', 'phone', 'address', 'account__username')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'ip_address', 'device', 'login_time')
    search_fields = ('account__username', 'ip_address', 'device')
    list_filter = ('login_time',)
    date_hierarchy = 'login_time'

admin.site.register(Account, AccountAdmin)
