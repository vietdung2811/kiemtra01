from django.contrib import admin
from django.urls import path, include
from api.views import customer_login, customer_home, customer_logout, product_search, add_to_cart, checkout, order_history, discard_cart, track_view

customer_patterns = [
    path('admin/', admin.site.urls), # Admin under /customer/ prefix
    path('login/', customer_login, name='login'),
    path('logout/', customer_logout, name='logout'),
    path('cart/', customer_home, name='customer_home'),
    path('search/', product_search, name='product_search'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('track-view/', track_view, name='track_view'),
    path('checkout/', checkout, name='checkout'),
    path('discard-cart/', discard_cart, name='discard_cart'),
    path('orders/', order_history, name='order_history'),
    path('', product_search, name='index'), # Root for customer
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/', include(customer_patterns)),
    path('', include(customer_patterns)),
]
