from django.db import models
from django.contrib.auth import get_user_model
from apps.agencies.models import Agency

User = get_user_model()

class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=150, unique=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Receipt(models.Model):
    receipt_date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ReceiptDetail(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        unique_together = ('receipt', 'item')

class Issue(models.Model):
    issue_date = models.DateField(auto_now_add=True)
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class IssueDetail(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        unique_together = ('issue', 'item')
