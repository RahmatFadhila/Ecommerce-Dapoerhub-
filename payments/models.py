from django.db import models
from django.conf import settings
from django.utils import timezone

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('midtrans', 'Midtrans (Kartu/E-Wallet/Transfer)'),
        ('bank_transfer', 'Transfer Bank Manual'),
        ('cash', 'Cash'),
        ('cod', 'Cash On Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu Pembayaran'),
        ('verifying', 'Sedang Diverifikasi'),
        ('success', 'Berhasil'),
        ('failed', 'Gagal'),
        ('refunded', 'Dikembalikan'),
        ('expired', 'Kadaluarsa'),
    ]

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='midtrans')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Fields untuk upload manual (backward compatibility)
    proof_image = models.ImageField(upload_to='payment_proofs/%Y/%m/', null=True, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    account_holder = models.CharField(max_length=200, blank=True)
    
    # ===== MIDTRANS FIELDS (NEW) =====
    midtrans_order_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    midtrans_snap_token = models.TextField(blank=True, null=True)
    midtrans_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    midtrans_transaction_status = models.CharField(max_length=50, blank=True, null=True)
    midtrans_payment_type = models.CharField(max_length=50, blank=True, null=True)
    midtrans_response = models.JSONField(blank=True, null=True)  # Simpan response lengkap
    
    transaction_id = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments'
    )

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment #{self.id} - {self.midtrans_order_id or 'No Order ID'}"

    def mark_as_success(self, verified_by=None):
        """Mark payment as successful"""
        self.status = 'success'
        self.verified_at = timezone.now()
        self.verified_by = verified_by
        self.save()
        
        if self.order:
            self.order.status = 'paid'
            self.order.paid_at = timezone.now()
            self.order.save()

    def mark_as_failed(self, reason=''):
        """Mark payment as failed"""
        self.status = 'failed'
        self.admin_notes = reason
        self.save()

    def mark_as_expired(self):
        """Mark payment as expired"""
        self.status = 'expired'
        self.save()
        
        if self.order:
            self.order.status = 'cancelled'
            self.order.save()