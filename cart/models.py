#cart/models.py
from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    """Keranjang belanja per user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart - {self.user.username}"

    @property
    def total_items(self):
        """Total jumlah item di cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Total harga sebelum ongkir"""
        return sum(item.total_price for item in self.items.all())

    def clear(self):
        """Kosongkan cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Item di dalam keranjang"""
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=10)
    price_per_portion = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        help_text="Harga per porsi saat ditambahkan ke cart",
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, help_text="Catatan khusus untuk pesanan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.cart.user.username}"

    @property
    def total_price(self):
        """Total harga item ini"""
        # ✅ FIX: Handle None value
        if self.price_per_portion:
            return self.price_per_portion * self.quantity
        elif self.product and self.product.price:
            return self.product.price * self.quantity
        return 0

    def save(self, *args, **kwargs):
        """Auto-fill price dari product saat save"""
        if not self.price_per_portion and self.product:
            self.price_per_portion = self.product.price
        super().save(*args, **kwargs)