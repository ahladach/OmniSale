from django.db import models

class Stock(models.Model):
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    product = models.CharField(max_length=100) 
    units = models.CharField(max_length=10, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    threshold = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.product