from django.db import models
from django.contrib.auth.models import User

class ProductChangeLog(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50) # 'add', 'update'
    product_type = models.CharField(max_length=20)
    product_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
