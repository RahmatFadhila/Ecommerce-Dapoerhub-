#orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem
from cart.models import Cart
from payments.models import Payment
from products.models import Product
from datetime import datetime, timedelta

@login_required
def checkout_from_cart(request):
    """
    ✅ CHECKOUT DARI CART - LANGSUNG KONFIRMASI (TANPA FORM PANJANG)
    """
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Keranjang belanja kosong')
        return redirect('cart')
    
    if request.method == 'POST':
        # Ambil data minimal dari POST
        delivery_date = request.POST.get('delivery_date')
        delivery_method = request.POST.get('delivery_method', 'delivery')
        notes = request.POST.get('notes', '')
        
        # Hitung total
        subtotal = cart.subtotal
        delivery_fee = 15000 if delivery_method == 'delivery' else 0
        total = subtotal + delivery_fee
        
        # Buat order (ambil data dari user profile)
        order = Order.objects.create(
            user=request.user,
            customer_name=request.user.get_full_name() or request.user.username,
            customer_phone=request.user.phone_number or '-',
            customer_email=request.user.email,
            delivery_method=delivery_method,
            delivery_address=request.user.address or '-',
            delivery_location=f"{request.user.city}, {request.user.postal_code}" if request.user.city else 'Makassar',
            delivery_date=delivery_date,
            delivery_time='10:00',
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
            notes=notes,
        )
        
        # Buat order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.price_per_portion,
                quantity=cart_item.quantity,
                notes=cart_item.notes
            )
        
        # Buat payment
        Payment.objects.create(
            order=order,
            payment_method='pending',
            amount=total,
        )
        
        # Kosongkan cart
        cart.clear()
        
        messages.success(request, f'🎉 Pesanan berhasil dibuat! Order: {order.order_number}')
        
        # LANGSUNG KE PAYMENT PAGE
        return redirect('payment_detail', order_id=order.id)
    
    # GET request - tampilkan halaman konfirmasi
    min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'min_date': min_date,
        'user': request.user,
    }
    return render(request, 'orders/checkout_confirm.html', context)


@login_required
def checkout_direct(request, product_id):
    """Checkout langsung - TETAP SAMA"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 10))
        price_per_portion = float(request.POST.get('price_per_portion', product.price))
        customer_name = request.POST.get('customer_name', request.user.get_full_name())
        customer_phone = request.POST.get('customer_phone', request.user.phone_number)
        customer_email = request.POST.get('customer_email', request.user.email)
        delivery_date = request.POST.get('delivery_date')
        delivery_location = request.POST.get('location', '')
        delivery_address = request.POST.get('address', '')
        notes = request.POST.get('notes', '')
        
        subtotal = price_per_portion * quantity
        delivery_fee = 15000
        total = subtotal + delivery_fee
        
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            delivery_method='delivery',
            delivery_address=delivery_address,
            delivery_location=delivery_location,
            delivery_date=delivery_date,
            delivery_time='10:00',
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=total,
            notes=notes,
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_price=price_per_portion,
            quantity=quantity,
        )
        
        Payment.objects.create(
            order=order,
            payment_method='pending',
            amount=total,
        )
        
        messages.success(request, f'Pesanan berhasil! Order: {order.order_number}')
        return redirect('payment_detail', order_id=order.id)
    
    return redirect('checkout', product_id=product.id)


@login_required
def order_list(request):
    """Daftar pesanan"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Detail pesanan"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'orders/order_detail.html', context)