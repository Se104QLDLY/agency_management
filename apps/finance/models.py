from django.db import models
from django.contrib.auth import get_user_model
from apps.agencies.models import Agency

User = get_user_model()

class Payment(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_date = models.DateField(auto_now_add=True)
    amount_collected = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is None:  # chỉ giảm nợ khi tạo mới
            self.agency.debt -= self.amount_collected
            self.agency.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.agency.name} - {self.amount_collected} VNĐ"

    class Meta:
        db_table = 'finance.Payment'

class Report(models.Model):
    report_type = models.CharField(max_length=50)
    report_date = models.DateField(auto_now_add=True)
    data = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance.Report'

class DebtTransaction(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)
    reference_id = models.IntegerField(null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'finance.DebtTransaction'
