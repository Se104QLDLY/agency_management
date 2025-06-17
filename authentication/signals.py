# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Account
from apps.agencies.models import Agency

@receiver(post_save, sender=User)
def create_default_agency_for_agent(sender, instance, created, **kwargs):
    if created and instance.account.account_role == Account.AGENT:
        from django.db import transaction
        # Đảm bảo chỉ tạo nếu chưa có agency nào gắn user này
        if not Agency.objects.filter(user_id=instance.user_id).exists():
            with transaction.atomic():
                Agency.objects.create(
                    agency_name="",
                    agency_type_id=None,
                    phone_number="",
                    address="",
                    district_id=None,
                    email=None,
                    representative=None,
                    reception_date=None,
                    debt_amount=0,
                    created_at=None,
                    updated_at=None,
                    user_id=instance.user_id
                )