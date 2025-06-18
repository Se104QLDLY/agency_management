from django.contrib import admin
from .models import Account, User

class UserInline(admin.TabularInline):
    model = User
    extra = 0
    fields = ('full_name', 'email', 'phone_number', 'address', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    '''Admin interface for Account model.'''
    list_display = ('account_id', 'username', 'account_role', 'created_at', 'updated_at')
    search_fields = ('username',)
    list_filter = ('account_role', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [UserInline]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    '''Admin interface for User model.'''
    list_display = ('user_id', 'full_name', 'email', 'phone_number', 'account', 'created_at', 'updated_at')
    search_fields = ('full_name', 'email', 'phone_number')
    list_filter = ('account', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
