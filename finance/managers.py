# managers.py
from django.db import models
from django.utils import timezone
from django.apps import apps

class ReportManager(models.Manager):
    def create_debt_report(self, for_date, created_by):
        DebtSummary = apps.get_model('finance', 'DebtSummary')
        summary = list(DebtSummary.objects.all().values('agency_id', 'agency_name', 'debt_amount'))
        return self.create(
            report_type='debt',
            report_date=for_date,
            data=summary,
            created_by=created_by
        )

    def create_sales_report(self, for_month, created_by):
        SalesMonthly = apps.get_model('finance', 'SalesMonthly')
        sales = list(SalesMonthly.objects.filter(month=for_month).values('month', 'total_sales'))
        return self.create(
            report_type='sales',
            report_date=for_month + "-01",
            data=sales,
            created_by=created_by
        )