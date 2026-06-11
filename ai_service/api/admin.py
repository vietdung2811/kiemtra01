from django.contrib import admin
from .models import ProductMetadata, UserViewLog

@admin.register(ProductMetadata)
class ProductMetadataAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'brand', 'name', 'price')
    list_filter = ('product_type', 'brand')

@admin.register(UserViewLog)
class UserViewLogAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'product_type', 'product_id', 'viewed_at')
    list_filter = ('product_type', 'viewed_at')
