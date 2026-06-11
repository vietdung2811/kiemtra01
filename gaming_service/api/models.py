from django.db import models

class Gaming(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.brand} {self.name}"
