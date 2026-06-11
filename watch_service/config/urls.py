from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import WatchViewSet

router = DefaultRouter()
router.register(r'watches', WatchViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
