from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import TabletViewSet

router = DefaultRouter()
router.register(r'tablets', TabletViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
