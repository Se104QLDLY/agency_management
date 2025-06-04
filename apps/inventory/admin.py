from django.contrib import admin
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit', 'price', 'stock_quantity', 'description')
    search_fields = ('name', 'description')
    list_filter = ('unit',)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_amount')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(ReceiptDetail)
class ReceiptDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'receipt', 'item', 'quantity', 'unit_price', 'line_total')
    search_fields = ('receipt__id', 'item__name')
    list_filter = ('item',)

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'agency', 'created_at', 'total_amount')
    search_fields = ('user__username', 'agency__name')
    list_filter = ('created_at', 'agency')
    date_hierarchy = 'created_at'

@admin.register(IssueDetail)
class IssueDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue', 'item', 'quantity', 'unit_price', 'line_total')
    search_fields = ('issue__id', 'item__name')
    list_filter = ('item',)
