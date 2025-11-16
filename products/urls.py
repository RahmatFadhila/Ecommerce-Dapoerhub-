from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu_list, name='menu'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    
    # Review
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # Redirect product detail ke checkout
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]