from django.contrib import admin
from django.urls import path, include
from api.views import staff_login, staff_home, staff_logout, add_item, update_item, delete_item

staff_patterns = [
    path('admin/', admin.site.urls),
    path('', staff_home, name='staff_home'),
    path('login/', staff_login, name='login'),
    path('logout/', staff_logout, name='logout'),
    path('add/', add_item, name='add_item'),
    path('update/<str:product_type>/<int:product_id>/', update_item, name='update_item'),
    path('delete/<str:product_type>/<int:product_id>/', delete_item, name='delete_item'),
]

urlpatterns = [
    path('staff/', include(staff_patterns)),
    path('', include(staff_patterns)),
]
