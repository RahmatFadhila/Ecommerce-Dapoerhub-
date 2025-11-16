from django.db import models
from django.conf import settings
from products.models import Product
from django.utils import timezone
import uuid

class Order(models.Model):
    """Model untuk pesanan catering"""
    
    STATUS_CHOICES = [
        ('pending', 'Menunggu Pembayaran'),
        ('paid', 'Sudah Dibayar'),
        ('processing', 'Sedang Diproses'),
        ('ready', 'Siap Dikirim'),
        ('delivering', 'Dalam Pengiriman'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Ambil Sendiri'),
        ('delivery', 'Diantar'),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField()
    
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='delivery')
    delivery_address = models.TextField()
    delivery_location = models.CharField(max_length=500, blank=True)
    delivery_date = models.DateField()
    delivery_time = models.TimeField(default='10:00')
    
    # ✅ FIX: Tambahkan default=0
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(uuid.uuid4().hex)[:4].upper()
            self.order_number = f"DH-{date_str}-{random_str}"
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        """Total porsi dalam order"""
        return sum(item.quantity for item in self.items.all())

    def calculate_total(self):
        """Hitung ulang total"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total = self.subtotal + self.delivery_fee
        self.save()


class OrderItem(models.Model):
    """Item dalam pesanan"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    product_name = models.CharField(max_length=200)
    # ✅ FIX: Tambahkan default=0
    product_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    quantity = models.PositiveIntegerField(default=10)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['id']

    def __str__(self):
        return f"{self.product_name} x{self.quantity} porsi"

    @property
    def total_price(self):
        # ✅ FIX: Handle None values
        price = self.product_price if self.product_price else 0
        qty = self.quantity if self.quantity else 0
        return price * qty

    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name = self.product.name
            self.product_price = self.product.price
        super().save(*args, **kwargs)