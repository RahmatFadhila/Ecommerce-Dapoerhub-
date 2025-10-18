from django.contrib import admin
from django.urls import path, include
from . import views  # ← TAMBAHKAN INI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),  # ← TAMBAHKAN INI (untuk homepage)
    path('users/', include('users.urls')),
    path('payments/', include('payments.urls')),
]