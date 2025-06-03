from django.db import models
from django.conf import settings

class Regulation(models.Model):
    key = models.CharField(max_length=50, primary_key=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
