# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .managers import ReportManager


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
    ]
    
    payment_id = models.AutoField(primary_key=True, db_column="payment_id")
    payment_date = models.DateField(db_column="payment_date")
    agency_id = models.IntegerField(db_column="agency_id")
    user_id = models.IntegerField(db_column="user_id")
    amount_collected = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        db_column="amount_collected",
        help_text="Số tiền thu được"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        db_column="status",
        help_text="Trạng thái thanh toán"
    )
    status_reason = models.TextField(db_column="status_reason", null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")

    class Meta:
        db_table = '"finance"."payment"'
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["agency_id"]),
            models.Index(fields=["user_id"]),
        ]
        managed = False

    def clean(self):
        from agency.models import Agency
        from decimal import Decimal
        
        # Validate amount is positive
        if self.amount_collected and self.amount_collected <= 0:
            raise ValidationError({'amount_collected': _('Payment amount must be greater than 0.')})
            
        # Validate payment doesn't exceed agency debt (only for confirmed payments)
        if self.status == 'confirmed':
            try:
                agency = Agency.objects.get(pk=self.agency_id)
                if self.amount_collected > agency.debt_amount:
                    raise ValidationError({
                        'amount_collected': _(
                            f'Payment amount ({self.amount_collected}) cannot exceed '
                            f'agency debt ({agency.debt_amount}).'
                        )
                    })
            except Agency.DoesNotExist:
                raise ValidationError({'agency_id': _('Agency does not exist.')})

    def __str__(self):
        return f"Payment #{self.payment_id} - Agency {self.agency_id} - {self.amount_collected}"


class Report(models.Model):
    SALES = 'sales'
    DEBT = 'debt'
    REPORT_TYPE_CHOICES = [
        (SALES, 'Sales'),
        (DEBT, 'Debt'),
    ]

    report_id = models.AutoField(primary_key=True, db_column="report_id")
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, db_column="report_type")
    report_date = models.DateField(db_column="report_date")
    data = models.JSONField(db_column="data")
    created_by = models.IntegerField(db_column="created_by")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")

    objects = ReportManager()

    class Meta:
        db_table = '"finance"."report"'
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["report_type"]),
            models.Index(fields=["created_by"]),
        ]
        managed = False

    def __str__(self):
        return f"Report #{self.report_id} - {self.report_type} ({self.report_date})"


class DebtSummary(models.Model):
    agency_id = models.IntegerField(db_column="agency_id", primary_key=True)
    agency_name = models.CharField(max_length=255, db_column="agency_name")
    debt_amount = models.DecimalField(max_digits=15, decimal_places=2, db_column="debt_amount")

    class Meta:
        managed = False
        db_table = '"finance"."v_debt_summary"'


class SalesMonthly(models.Model):
    month = models.CharField(max_length=7, db_column="month", primary_key=True)
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, db_column="total_sales")

    class Meta:
        managed = False
        db_table = '"finance"."v_sales_monthly"'

