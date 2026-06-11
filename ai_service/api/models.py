from django.db import models
from django.contrib.auth.models import User

class ProductMetadata(models.Model):
    product_id = models.IntegerField()
    product_type = models.CharField(max_length=20) # 'laptop' or 'mobile'
    brand = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    embedding = models.BinaryField(null=True, blank=True) # Store vector as binary

    class Meta:
        unique_together = ('product_id', 'product_type')

    def __str__(self):
        return f"{self.product_type} - {self.brand} {self.name}"

class UserViewLog(models.Model):
    user_id = models.IntegerField() # Store User ID from customer_service
    product_id = models.IntegerField()
    product_type = models.CharField(max_length=20)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} viewed {self.product_type} {self.product_id}"
