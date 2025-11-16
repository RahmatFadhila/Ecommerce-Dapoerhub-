from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, CustomPasswordChangeForm
from .models import CustomUser


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Selamat datang {user.username}! Akun Anda berhasil dibuat.')
            return redirect('profile')
        else:
            messages.error(request, 'Terjadi kesalahan. Mohon periksa form Anda.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!')
            
            # Redirect to 'next' parameter or profile
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah!')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Anda telah berhasil keluar.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    context = {
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
            return redirect('profile')
        else:
            messages.error(request, 'Terjadi kesalahan. Mohon periksa form Anda.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password Anda berhasil diubah!')
            return redirect('profile')
        else:
            messages.error(request, 'Terjadi kesalahan. Mohon periksa form Anda.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


@login_required
def delete_account_view(request):
    """Delete user account view"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Akun Anda telah dihapus.')
        return redirect('home')
    
    return render(request, 'users/delete_account.html')