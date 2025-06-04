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

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile)
admin.site.register(LoginHistory)
