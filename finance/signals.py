# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment

@receiver(post_save, sender=Payment)
def update_agency_debt_on_payment(sender, instance, **kwargs):
    from agency.signals import _update_debt_amount
    _update_debt_amount(instance.agency_id)