# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.validators import MinValueValidator
from .managers import ItemQuerySet


class Unit(models.Model):
    unit_id = models.AutoField(primary_key=True, db_column="unit_id")
    unit_name = models.CharField(max_length=50, unique=True, db_column="unit_name")

    class Meta:
        db_table = '"inventory"."unit"'
        ordering = ["unit_name"]
        managed = False

    def __str__(self):
        return self.unit_name


class Item(models.Model):
    item_id = models.AutoField(primary_key=True, db_column="item_id")
    item_name = models.CharField(max_length=150, unique=True, db_column="item_name")
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT, db_column="unit_id", related_name="items")
    price = models.DecimalField(
        max_digits=15, decimal_places=2, db_column="price",
        validators=[MinValueValidator(0.01)]
    )
    stock_quantity = models.PositiveIntegerField(db_column="stock_quantity")
    description = models.TextField(null=True, blank=True, db_column="description")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")
    updated_at = models.DateTimeField(null=True, blank=True, db_column="updated_at")

    objects = ItemQuerySet.as_manager()

    class Meta:
        db_table = '"inventory"."item"'
        ordering = ["item_name"]
        indexes = [
            models.Index(fields=["unit"]),
        ]
        managed = False

    def __str__(self):
        return self.item_name


class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True, db_column="receipt_id")
    receipt_date = models.DateField(db_column="receipt_date")
    user_id = models.IntegerField(db_column="user_id")
    agency_id = models.IntegerField(db_column="agency_id")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, db_column="total_amount")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")

    class Meta:
        db_table = '"inventory"."receipt"'
        ordering = ["-receipt_date"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["agency_id"]),
        ]
        managed = False

    def __str__(self):
        return f"Receipt #{self.receipt_id}"


class ReceiptDetail(models.Model):
    receipt_detail_id = models.AutoField(primary_key=True, db_column="receipt_detail_id")
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, db_column="receipt_id", related_name="details")
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, db_column="item_id", related_name="receipt_details")
    quantity = models.PositiveIntegerField(db_column="quantity", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, db_column="unit_price", validators=[MinValueValidator(0.01)])
    line_total = models.DecimalField(max_digits=18, decimal_places=2, db_column="line_total", validators=[MinValueValidator(0.01)])

    class Meta:
        db_table = '"inventory"."receiptdetail"'
        unique_together = ("receipt", "item")
        ordering = ["receipt", "item"]
        indexes = [
            models.Index(fields=["receipt"]),
            models.Index(fields=["item"]),
        ]
        managed = False

    def __str__(self):
        return f"ReceiptDetail #{self.receipt_detail_id}"


class Issue(models.Model):
    issue_id = models.AutoField(primary_key=True, db_column="issue_id")
    issue_date = models.DateField(db_column="issue_date")
    agency_id = models.IntegerField(db_column="agency_id")
    user_id = models.IntegerField(db_column="user_id")
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, db_column="total_amount")
    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")

    class Meta:
        db_table = '"inventory"."issue"'
        ordering = ["-issue_date"]
        indexes = [
            models.Index(fields=["agency_id"]),
            models.Index(fields=["user_id"]),
        ]
        managed = False

    def __str__(self):
        return f"Issue #{self.issue_id}"


class IssueDetail(models.Model):
    issue_detail_id = models.AutoField(primary_key=True, db_column="issue_detail_id")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, db_column="issue_id", related_name="details")
    item = models.ForeignKey(Item, on_delete=models.RESTRICT, db_column="item_id", related_name="issue_details")
    quantity = models.PositiveIntegerField(db_column="quantity", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, db_column="unit_price", validators=[MinValueValidator(0.01)])
    line_total = models.DecimalField(max_digits=18, decimal_places=2, db_column="line_total", validators=[MinValueValidator(0.01)])

    class Meta:
        db_table = '"inventory"."issuedetail"'
        unique_together = ("issue", "item")
        ordering = ["issue", "item"]
        indexes = [
            models.Index(fields=["issue"]),
            models.Index(fields=["item"]),
        ]
        managed = False

    def __str__(self):
        return f"IssueDetail #{self.issue_detail_id}"

