from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'agency', 'user', 'payment_date', 'amount_collected', 'created_at')
    search_fields = ('agency__name', 'user__username')
    list_filter = ('payment_date', 'agency')
    date_hierarchy = 'payment_date'
