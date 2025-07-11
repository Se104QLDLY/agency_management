# signals.py
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Payment

@receiver(post_save, sender=Payment)
def update_agency_debt_on_payment(sender, instance: Payment, created: bool, **kwargs):
    """
    DISABLED: Debt update is now handled by database trigger f_update_debt_amount()
    This signal is kept for reference but does nothing to avoid double deduction.
    """
    return  # Early return to disable this signal
        
    with transaction.atomic():
        from agency.models import Agency
        agency = Agency.objects.select_for_update().get(pk=instance.agency_id)
        
        current_debt = agency.debt_amount or Decimal("0.00")
        payment_amount = instance.amount_collected or Decimal("0.00")
        
        # Validate payment amount doesn't exceed current debt
        if payment_amount > current_debt:
            raise ValidationError(
                f"Số tiền thanh toán ({payment_amount}) không thể lớn hơn "
                f"công nợ hiện tại ({current_debt})"
            )
        
        # Validate payment amount is positive
        if payment_amount <= 0:
            raise ValidationError("Số tiền thanh toán phải lớn hơn 0")
        
        # Update debt
        new_debt = current_debt - payment_amount
        
        # Ensure debt doesn't go negative (additional safety check)
        if new_debt < 0:
            new_debt = Decimal("0.00")
            
        agency.debt_amount = new_debt
        agency.save(update_fields=["debt_amount"])