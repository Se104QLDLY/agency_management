from django.contrib import admin
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail

admin.site.register(Unit)
admin.site.register(Item)
admin.site.register(Receipt)
admin.site.register(ReceiptDetail)
admin.site.register(Issue)
admin.site.register(IssueDetail)
