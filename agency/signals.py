# signals.py
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.inventory.models import Issue
from apps.finance.models import Payment
from .models import Agency

@receiver(post_save, sender=Issue)
def update_agency_debt_on_issue(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            agency = Agency.objects.select_for_update().get(pk=instance.agency_id)
            new_debt = agency.debt_amount + instance.total_amount
            if new_debt > agency.agency_type.max_debt:
                raise ValueError("Vượt quá giới hạn nợ cho phép của đại lý!")
            agency.debt_amount = new_debt
            agency.save(update_fields=["debt_amount"])

@receiver(post_save, sender=Payment)
def update_agency_debt_on_payment(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            agency = Agency.objects.select_for_update().get(pk=instance.agency_id)
            agency.debt_amount = agency.debt_amount - instance.amount_collected
            agency.save(update_fields=["debt_amount"])