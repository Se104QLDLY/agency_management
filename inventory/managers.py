# managers.py
from django.db import models

class ItemQuerySet(models.QuerySet):
    def low_stock(self, threshold=10):
        return self.filter(stock_quantity__lte=threshold, stock_quantity__gt=0)

    def out_of_stock(self):
        return self.filter(stock_quantity=0)