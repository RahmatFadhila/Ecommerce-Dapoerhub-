from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/cart/', views.checkout_from_cart, name='checkout_from_cart'),
    path('checkout/<int:product_id>/', views.checkout_direct, name='checkout_direct'),
]