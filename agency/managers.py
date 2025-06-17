# managers.py
from django.db import models
from django.db.models import F

class AgencyQuerySet(models.QuerySet):
    def in_debt(self):
        return self.filter(debt_amount__gt=0)

    def over_limit(self):
        return self.filter(debt_amount__gt=F("agency_type__max_debt"))