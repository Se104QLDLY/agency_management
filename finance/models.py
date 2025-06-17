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
    payment_id = models.AutoField(primary_key=True, db_column="payment_id")
    payment_date = models.DateField(db_column="payment_date")
    agency_id = models.IntegerField(db_column="agency_id")
    user_id = models.IntegerField(db_column="user_id")
    amount_collected = models.DecimalField(max_digits=15, decimal_places=2, db_column="amount_collected")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")

    class Meta:
        db_table = "payment"
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["agency_id"]),
            models.Index(fields=["user_id"]),
        ]

    def clean(self):
        from agency.models import Agency
        try:
            agency = Agency.objects.get(pk=self.agency_id)
            if self.amount_collected > agency.debt_amount:
                raise ValidationError({'amount_collected': _('Collected amount cannot exceed agency debt.')})
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
        db_table = "report"
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["report_type"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"Report #{self.report_id} - {self.report_type} ({self.report_date})"


class DebtSummary(models.Model):
    agency_id = models.IntegerField(db_column="agency_id", primary_key=True)
    agency_name = models.CharField(max_length=255, db_column="agency_name")
    debt_amount = models.DecimalField(max_digits=15, decimal_places=2, db_column="debt_amount")

    class Meta:
        managed = False
        db_table = "v_debt_summary"


class SalesMonthly(models.Model):
    month = models.CharField(max_length=7, db_column="month", primary_key=True)
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, db_column="total_sales")

    class Meta:
        managed = False
        db_table = "v_sales_monthly"

