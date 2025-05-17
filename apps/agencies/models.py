from django.db import models

class District(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    max_agencies = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.city}"

class AgencyType(models.Model):
    type_name = models.CharField(max_length=100)
    max_debt = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.type_name

class Agency(models.Model):
    name = models.CharField(max_length=150)
    agency_type = models.ForeignKey(AgencyType, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    representative = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name
