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
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return f"Phiếu nhập #{self.id}"

class ReceiptDetail(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=18, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # cập nhật tồn kho
        self.item.stock_quantity += self.quantity
        self.item.save()

class Issue(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return f"Phiếu xuất #{self.id}"

class IssueDetail(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=18, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        if self.quantity > self.item.stock_quantity:
            raise ValueError("Số lượng xuất vượt quá tồn kho")
        super().save(*args, **kwargs)
        # cập nhật tồn kho và công nợ
        self.item.stock_quantity -= self.quantity
        self.item.save()
        self.issue.agency.debt += self.line_total
        self.issue.agency.save()
