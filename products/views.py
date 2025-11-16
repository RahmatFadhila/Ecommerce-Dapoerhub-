from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Review, Category
from decimal import Decimal


def home(request):
    """Homepage - TETAP BISA DIAKSES TANPA LOGIN"""
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(
        status='active',
        is_featured=True
    ).select_related('category')[:8]
    
    context = {
        'categories': categories,
        'products': products,
        'show_search': False,  # ← SEARCH BAR TIDAK MUNCUL
    }
    return render(request, 'home.html', context)


@login_required
def menu_list(request):
    """Menu page - WAJIB LOGIN"""
    products = Product.objects.filter(status='active').select_related('category')
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'show_search': True,  # ← SEARCH BAR MUNCUL DI MENU
    }
    return render(request, 'menu.html', context)


@login_required
def checkout(request, product_id):
    """Checkout page - WAJIB LOGIN"""
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    
    base_price = product.price
    mid_price = base_price * Decimal('0.8')
    low_price = base_price * Decimal('0.6')
    
    context = {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'price_high': int(base_price),
        'price_mid': int(mid_price),
        'price_low': int(low_price),
        'show_search': False,  # ← SEARCH BAR TIDAK MUNCUL
    }
    return render(request, 'checkout.html', context)


def contact(request):
    """Contact page"""
    context = {
        'show_search': False,  # ← SEARCH BAR TIDAK MUNCUL
    }
    return render(request, 'contact.html', context)


@login_required
def product_detail(request, pk):
    """Redirect ke checkout"""
    return redirect('checkout', product_id=pk)


@login_required
def add_review(request, product_id):
    """Add or update review"""
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, 'Review berhasil ditambahkan!')
        else:
            messages.error(request, 'Rating dan komentar harus diisi!')
    
    return redirect('checkout', product_id=product_id)