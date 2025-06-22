from django.contrib import admin
from .models import Unit, Item, Receipt, Receiptdetail, Issue, Issuedetail

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0
    fields = ("item_name", "unit", "price", "stock_quantity")
    show_change_link = True

class ReceiptdetailInline(admin.TabularInline):
    model = Receiptdetail
    extra = 0
    fields = ("item", "quantity", "unit_price", "line_total")
    show_change_link = True

class IssuedetailInline(admin.TabularInline):
    model = Issuedetail
    extra = 0
    fields = ("item", "quantity", "unit_price", "line_total")
    show_change_link = True

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin interface for Unit model."""
    list_display = ("unit_id", "unit_name")
    search_fields = ("unit_name",)
    inlines = [ItemInline]

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for Item model."""
    list_display = ("item_id", "item_name", "unit", "price", "stock_quantity")
    search_fields = ("item_name",)
    list_filter = ("unit",)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Admin interface for Receipt model."""
    list_display = ("receipt_id", "receipt_date", "user_id", "agency_id", "total_amount", "created_at")
    search_fields = ("user_id", "agency_id")
    list_filter = ("receipt_date",)
    readonly_fields = ("created_at",)
    inlines = [ReceiptdetailInline]

@admin.register(Receiptdetail)
class ReceiptdetailAdmin(admin.ModelAdmin):
    """Admin interface for Receiptdetail model."""
    list_display = ("receipt_detail_id", "receipt", "item", "quantity", "unit_price", "line_total")
    search_fields = ("receipt__receipt_id", "item__item_name")
    list_filter = ("receipt", "item")

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Admin interface for Issue model."""
    list_display = ("issue_id", "issue_date", "agency_id", "user_id", "total_amount", "created_at")
    search_fields = ("agency_id", "user_id")
    list_filter = ("issue_date",)
    readonly_fields = ("created_at",)
    inlines = [IssuedetailInline]

@admin.register(Issuedetail)
class IssuedetailAdmin(admin.ModelAdmin):
    """Admin interface for Issuedetail model."""
    list_display = ("issue_detail_id", "issue", "item", "quantity", "unit_price", "line_total")
    search_fields = ("issue__issue_id", "item__item_name")
    list_filter = ("issue", "item")
