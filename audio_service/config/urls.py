from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import AudioViewSet

router = DefaultRouter()
router.register(r'audios', AudioViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
