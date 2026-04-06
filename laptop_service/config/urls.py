from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import LaptopViewSet

router = DefaultRouter()
router.register(r'laptops', LaptopViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
