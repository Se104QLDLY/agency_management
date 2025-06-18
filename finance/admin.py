from django.contrib import admin
from .models import Payment, Report, DebtSummary, SalesMonthly

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    '''Admin interface for Payment model.'''
    list_display = ('payment_id', 'payment_date', 'agency_id', 'user_id', 'amount_collected', 'created_at')
    search_fields = ('agency_id', 'user_id')
    list_filter = ('payment_date',)
    readonly_fields = ('created_at',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    '''Admin interface for Report model.'''
    list_display = ('report_id', 'report_type', 'report_date', 'created_by', 'created_at')
    search_fields = ('report_type', 'created_by')
    list_filter = ('report_type', 'report_date')
    readonly_fields = ('created_at',)

@admin.register(DebtSummary)
class DebtSummaryAdmin(admin.ModelAdmin):
    '''Read-only admin for DebtSummary view.'''
    list_display = ('agency_id', 'agency_name', 'debt_amount')
    search_fields = ('agency_name',)
    readonly_fields = ('agency_id', 'agency_name', 'debt_amount')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SalesMonthly)
class SalesMonthlyAdmin(admin.ModelAdmin):
    '''Read-only admin for SalesMonthly view.'''
    list_display = ('month', 'total_sales')
    search_fields = ('month',)
    readonly_fields = ('month', 'total_sales')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
