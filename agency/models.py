# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError
from .managers import AgencyQuerySet

class AgencyType(models.Model):
    agency_type_id = models.AutoField(primary_key=True, db_column="agency_type_id")
    type_name = models.CharField(max_length=50, unique=True, db_column="type_name")
    max_debt = models.DecimalField(max_digits=15, decimal_places=2, db_column="max_debt")
    description = models.TextField(null=True, db_column="description")

    class Meta:
        db_table = '"agency"."agencytype"'
        ordering = ["type_name"]
        managed = False

    def __str__(self):
        return self.type_name

class District(models.Model):
    district_id = models.AutoField(primary_key=True, db_column="district_id")
    city_name = models.CharField(max_length=100, null=True, db_column="city_name")
    district_name = models.CharField(max_length=100, unique=True, db_column="district_name")
    max_agencies = models.IntegerField(db_column="max_agencies")

    class Meta:
        db_table = '"agency"."district"'
        ordering = ["city_name", "district_name"]
        managed = False

    def __str__(self):
        return f"{self.district_name} ({self.city_name})"

class Agency(models.Model):
    agency_id = models.AutoField(primary_key=True, db_column="agency_id")
    agency_name = models.CharField(max_length=150, db_column="agency_name")
    agency_type = models.ForeignKey(
        AgencyType,
        on_delete=models.RESTRICT,
        db_column="agency_type_id",
        related_name="agencies"
    )
    phone_number = models.CharField(max_length=15, db_column="phone_number")
    address = models.CharField(max_length=255, db_column="address")
    district = models.ForeignKey(
        District,
        on_delete=models.RESTRICT,
        db_column="district_id",
        related_name="agencies"
    )
    email = models.CharField(max_length=100, unique=True, null=True, blank=True, db_column="email")
    representative = models.CharField(max_length=100, null=True, blank=True, db_column="representative")
    reception_date = models.DateField(db_column="reception_date")
    debt_amount = models.DecimalField(max_digits=15, decimal_places=2, db_column="debt_amount")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, db_column="created_at")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, db_column="updated_at")
    user_id = models.IntegerField(unique=True, null=True, blank=True, db_column="user_id")

    objects = AgencyQuerySet.as_manager()

    class Meta:
        db_table = '"agency"."agency"'
        ordering = ["agency_name"]
        indexes = [
            models.Index(fields=["agency_type"]),
            models.Index(fields=["district"]),
        ]
        managed = False

    def __str__(self):
        return self.agency_name

class StaffAgency(models.Model):
    staff_id = models.IntegerField(db_column="staff_id", primary_key=True)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        db_column="agency_id",
        related_name="staff_agency"
    )

    class Meta:
        db_table = '"agency"."staffagency"'
        constraints = [
            models.UniqueConstraint(fields=["staff_id", "agency"], name="unique_staff_agency")
        ]
        ordering = ["staff_id", "agency"]
        managed = False

    def __str__(self):
        return f"Staff {self.staff_id} - {self.agency.agency_name}"

    def clean(self):
        if StaffAgency.objects.filter(staff_id=self.staff_id, agency=self.agency).exclude(pk=self.pk).exists():
            raise ValidationError("Cặp staff–agency này đã tồn tại.")


