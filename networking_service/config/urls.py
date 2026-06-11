from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import NetworkingViewSet

router = DefaultRouter()
router.register(r'networking', NetworkingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
