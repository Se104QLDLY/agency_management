from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Regulation

@receiver(pre_save, sender=Regulation)
def update_regulation_timestamp(sender, instance, **kwargs):
    instance.updated_at = timezone.now()
    # Optional: Add logging here if needed