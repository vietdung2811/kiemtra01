from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import GamingViewSet

router = DefaultRouter()
router.register(r'gaming', GamingViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
