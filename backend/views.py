from django.shortcuts import render
from django.db.models import Sum
from users.models import CustomUser
from payments.models import Payment

def dashboard(request):
    total_users = CustomUser.objects.count()
    total_payments = Payment.objects.count()
    total_revenue = Payment.objects.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'total_users': total_users,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
    }
    return render(request, 'dashboard.html', context)