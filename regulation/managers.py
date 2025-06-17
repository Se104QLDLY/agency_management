from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class RegulationManager(models.Manager):
    def get(self, key, default=None):
        try:
            return super().get_queryset().get(regulation_key=key).regulation_value
        except ObjectDoesNotExist:
            return default

    def set(self, key, value, user=None):
        obj, created = self.update_or_create(
            regulation_key=key,
            defaults={
                'regulation_value': value,
                'last_updated_by': user.id if user else None,
                'updated_at': None,  # Will be set by signal
            }
        )
        return obj