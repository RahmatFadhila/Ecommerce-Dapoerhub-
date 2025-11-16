from django.urls import path
from . import views

urlpatterns = [
    # Payment list
    path('', views.payment_list, name='payment_list'),
    
    # Payment detail (Midtrans)
    path('<int:order_id>/', views.payment_detail, name='payment_detail'),
    
    # Midtrans callbacks
    path('notification/', views.midtrans_notification, name='midtrans_notification'),
    path('finish/', views.payment_finish, name='payment_finish'),
    path('error/', views.payment_error, name='payment_error'),
    path('pending/', views.payment_pending, name='payment_pending'),
    
    # Manual upload (backward compatibility)
    path('upload/<int:order_id>/', views.upload_payment_proof, name='upload_payment_proof'),
]