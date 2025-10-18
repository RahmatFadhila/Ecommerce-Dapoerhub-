from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser

def users_list(request):
    users = CustomUser.objects.all()
    return render(request, 'users/list.html', {'users': users})

def user_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        CustomUser.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        return redirect('users_list')
    
    return render(request, 'users/form.html')

def user_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.save()
        return redirect('users_list')
    
    return render(request, 'users/form.html', {'user': user})

def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.delete()
    return redirect('users_list')