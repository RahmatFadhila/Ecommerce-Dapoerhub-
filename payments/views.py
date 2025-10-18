from django.shortcuts import render, redirect, get_object_or_404
from .models import Payment
from users.models import CustomUser

def payments_list(request):
    payments = Payment.objects.all().select_related('user')
    return render(request, 'payments/list.html', {'payments': payments})

def payment_create(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        amount = request.POST.get('amount')
        status = request.POST.get('status')
        payment_method = request.POST.get('payment_method')
        description = request.POST.get('description')
        
        Payment.objects.create(
            user_id=user_id,
            amount=amount,
            status=status,
            payment_method=payment_method,
            description=description
        )
        return redirect('payments_list')
    
    users = CustomUser.objects.all()
    return render(request, 'payments/form.html', {'users': users})

def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        payment.user_id = request.POST.get('user')
        payment.amount = request.POST.get('amount')
        payment.status = request.POST.get('status')
        payment.payment_method = request.POST.get('payment_method')
        payment.description = request.POST.get('description')
        payment.save()
        return redirect('payments_list')
    
    users = CustomUser.objects.all()
    return render(request, 'payments/form.html', {'payment': payment, 'users': users})

def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.delete()
    return redirect('payments_list')