# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from .managers import RegulationManager

import re


class Regulation(models.Model):
    regulation_key = models.CharField(primary_key=True, max_length=50)
    regulation_value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    last_updated_by = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    objects = RegulationManager()

    class Meta:
        db_table = 'config"."regulation'
        ordering = ['regulation_key']
        verbose_name = 'Regulation'
        verbose_name_plural = 'Regulations'
        managed = False

    def clean(self):
        if not re.match(r'^[A-Za-z0-9_]+$', self.regulation_key):
            raise ValidationError({'regulation_key': 'Key must not contain special characters.'})
        if not self.regulation_value or not self.regulation_value.strip():
            raise ValidationError({'regulation_value': 'Value must not be empty.'})

    def __str__(self):
        return f"{self.regulation_key}: {self.regulation_value}"