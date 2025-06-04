from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Regulation(models.Model):
    regulation_key = models.CharField(max_length=50, primary_key=True)
    regulation_value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.regulation_key}: {self.regulation_value}"

    class Meta:
        db_table = 'config.Regulation'
