#cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from products.models import Product
from decimal import Decimal

@login_required
def cart_view(request):
    """Halaman keranjang belanja"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
    }
    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Tambah produk ke keranjang"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Get data from POST
        quantity = int(request.POST.get('quantity', 10))
        price_per_portion = Decimal(request.POST.get('price_per_portion', product.price))
        notes = request.POST.get('notes', '')
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price_per_portion': price_per_portion,
                'notes': notes
            }
        )
        
        if not created:
            # Item sudah ada, update quantity
            cart_item.quantity += quantity
            cart_item.price_per_portion = price_per_portion  # Update harga
            cart_item.notes = notes
            cart_item.save()
            messages.success(request, f'✅ {product.name} berhasil ditambahkan! Quantity diupdate.')
        else:
            messages.success(request, f'✅ {product.name} berhasil ditambahkan ke keranjang!')
        
        # AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Produk ditambahkan ke keranjang'})
        
        return redirect('cart')
    
    return redirect('menu')


@login_required
def update_cart_item(request, item_id):
    """Update quantity item di cart"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        action = request.POST.get('action')
        
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                messages.success(request, 'Item dihapus dari keranjang')
                return redirect('cart')
        
        cart_item.save()
        messages.success(request, 'Quantity berhasil diupdate')
    
    return redirect('cart')


@login_required
def remove_cart_item(request, item_id):
    """Hapus item dari cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'❌ {product_name} dihapus dari keranjang')
    return redirect('cart')


@login_required
def clear_cart(request):
    """Kosongkan seluruh cart"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart.clear()
        messages.success(request, 'Keranjang berhasil dikosongkan')
    
    return redirect('cart')