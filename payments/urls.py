from django.urls import path
from . import views

urlpatterns = [
    path('', views.payments_list, name='payments_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('edit/<int:pk>/', views.payment_edit, name='payment_edit'),
    path('delete/<int:pk>/', views.payment_delete, name='payment_delete'),
]