# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Item, Issuedetail, Receiptdetail, Receipt, Issue

@receiver(post_save, sender=Issuedetail)
def decrease_stock_on_issue(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            item = Item.objects.select_for_update().get(pk=instance.item_id)
            if item.stock_quantity < instance.quantity:
                raise ValidationError("Không đủ hàng trong kho để xuất.")
            item.stock_quantity -= instance.quantity
            item.save(update_fields=["stock_quantity"])

@receiver(post_save, sender=Receiptdetail)
def increase_stock_on_receipt(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            item = Item.objects.select_for_update().get(pk=instance.item_id)
            item.stock_quantity += instance.quantity
            item.save(update_fields=["stock_quantity"])

def update_receipt_total(receipt_id):
    receipt = Receipt.objects.get(pk=receipt_id)
    total = receipt.details.aggregate(models.Sum('line_total'))['line_total__sum'] or 0
    receipt.total_amount = total
    receipt.save(update_fields=["total_amount"])

def update_issue_total(issue_id):
    issue = Issue.objects.get(pk=issue_id)
    total = issue.details.aggregate(models.Sum('line_total'))['line_total__sum'] or 0
    issue.total_amount = total
    issue.save(update_fields=["total_amount"])

@receiver([post_save, post_delete], sender=Receiptdetail)
def recalc_receipt_total(sender, instance, **kwargs):
    update_receipt_total(instance.receipt_id)

@receiver([post_save, post_delete], sender=Issuedetail)
def recalc_issue_total(sender, instance, **kwargs):
    update_issue_total(instance.issue_id)