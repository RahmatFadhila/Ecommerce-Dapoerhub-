from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json

from .models import Payment
from orders.models import Order
from .midtrans_service import MidtransService


@login_required
def payment_detail(request, order_id):
    """
    Halaman pembayaran dengan Midtrans Snap
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get or create payment
    try:
        payment = order.payment
    except Payment.DoesNotExist:
        payment = Payment.objects.create(
            order=order,
            payment_method='midtrans',
            amount=order.total,
        )
    
    # Generate Snap Token jika belum ada
    if not payment.midtrans_snap_token:
        try:
            midtrans = MidtransService()
            transaction = midtrans.create_transaction(order, payment)
            payment.midtrans_snap_token = transaction['snap_token']
            payment.midtrans_order_id = transaction['order_id']
            payment.save()
        except Exception as e:
            messages.error(request, f'Gagal membuat pembayaran: {str(e)}')
            return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'payment': payment,
        'midtrans_client_key': settings.MIDTRANS_CLIENT_KEY,
        'midtrans_environment': 'sandbox' if not settings.MIDTRANS_IS_PRODUCTION else 'api',
    }
    return render(request, 'payments/payment_midtrans.html', context)


@csrf_exempt
def midtrans_notification(request):
    """
    Webhook untuk notifikasi dari Midtrans
    Dipanggil otomatis oleh Midtrans saat ada perubahan status pembayaran
    """
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    
    try:
        # Parse notification body
        notification = json.loads(request.body)
        
        order_id = notification.get('order_id')
        transaction_status = notification.get('transaction_status')
        fraud_status = notification.get('fraud_status', 'accept')
        signature_key = notification.get('signature_key')
        
        # Verify signature
        midtrans = MidtransService()
        gross_amount = notification.get('gross_amount')
        status_code = notification.get('status_code')
        
        expected_signature = midtrans.verify_signature(
            order_id, status_code, gross_amount, settings.MIDTRANS_SERVER_KEY
        )
        
        if signature_key != expected_signature:
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=403)
        
        # Get payment object
        try:
            payment = Payment.objects.get(midtrans_order_id=order_id)
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
        
        # Update payment details
        payment.midtrans_transaction_id = notification.get('transaction_id')
        payment.midtrans_transaction_status = transaction_status
        payment.midtrans_payment_type = notification.get('payment_type')
        payment.midtrans_response = notification
        
        # Handle transaction status
        if transaction_status == 'capture':
            if fraud_status == 'accept':
                payment.mark_as_success()
        elif transaction_status == 'settlement':
            payment.mark_as_success()
        elif transaction_status == 'pending':
            payment.status = 'pending'
            payment.save()
        elif transaction_status in ['deny', 'cancel']:
            payment.mark_as_failed(f'Transaction {transaction_status}')
        elif transaction_status == 'expire':
            payment.mark_as_expired()
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        print(f"Error processing Midtrans notification: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def payment_finish(request):
    """Halaman setelah pembayaran selesai (redirect dari Midtrans)"""
    order_id = request.GET.get('order_id')
    
    if order_id:
        try:
            payment = Payment.objects.get(midtrans_order_id=order_id)
            
            # Check status dari Midtrans
            midtrans = MidtransService()
            status = midtrans.get_transaction_status(order_id)
            
            if status:
                transaction_status = status.get('transaction_status')
                
                if transaction_status in ['capture', 'settlement']:
                    messages.success(request, '✅ Pembayaran berhasil! Pesanan sedang diproses.')
                elif transaction_status == 'pending':
                    messages.info(request, '⏳ Pembayaran pending. Silakan selesaikan pembayaran Anda.')
                else:
                    messages.warning(request, f'Status pembayaran: {transaction_status}')
            
            return redirect('order_detail', order_id=payment.order.id)
        
        except Payment.DoesNotExist:
            messages.error(request, 'Payment tidak ditemukan')
    
    return redirect('order_list')


@login_required
def payment_error(request):
    """Halaman saat pembayaran error"""
    messages.error(request, '❌ Pembayaran gagal. Silakan coba lagi.')
    
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            payment = Payment.objects.get(midtrans_order_id=order_id)
            return redirect('payment_detail', order_id=payment.order.id)
        except Payment.DoesNotExist:
            pass
    
    return redirect('order_list')


@login_required
def payment_pending(request):
    """Halaman saat pembayaran pending"""
    messages.info(request, '⏳ Pembayaran pending. Silakan selesaikan pembayaran Anda.')
    
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            payment = Payment.objects.get(midtrans_order_id=order_id)
            return redirect('order_detail', order_id=payment.order.id)
        except Payment.DoesNotExist:
            pass
    
    return redirect('order_list')


@login_required
def payment_list(request):
    """Daftar pembayaran user"""
    payments = Payment.objects.filter(order__user=request.user).order_by('-payment_date')
    
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment_list.html', context)


# ===== BACKWARD COMPATIBILITY: Manual Upload =====
@login_required
def upload_payment_proof(request, order_id):
    """Upload bukti pembayaran manual (untuk metode transfer bank)"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment = order.payment
        
        payment_method = request.POST.get('payment_method', 'bank_transfer')
        payment.payment_method = payment_method
        
        if payment_method == 'bank_transfer':
            payment.bank_name = request.POST.get('bank_name', '')
            payment.account_holder = request.POST.get('account_holder', '')
            
            if 'proof_image' in request.FILES:
                payment.proof_image = request.FILES['proof_image']
                payment.status = 'verifying'
                messages.success(request, '✅ Bukti transfer berhasil diupload! Sedang diverifikasi.')
            else:
                messages.warning(request, '⚠️ Mohon upload bukti transfer!')
                return redirect('payment_detail', order_id=order.id)
        
        payment.save()
        
        if payment.status == 'verifying':
            order.status = 'processing'
            order.save()
        
        return redirect('order_detail', order_id=order.id)
    
    return redirect('payment_detail', order_id=order_id)