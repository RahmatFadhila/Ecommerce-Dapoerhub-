from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    # Validator untuk nomor telepon
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Nomor telepon harus dalam format: '+999999999'. Maksimal 15 digit."
    )
    
    # Field tambahan
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name="Nomor Telepon"
    )
    profile_picture = models.ImageField(
        upload_to='profiles/%Y/%m/%d/', 
        blank=True, 
        null=True,
        verbose_name="Foto Profil"
    )
    date_of_birth = models.DateField(
        blank=True, 
        null=True,
        verbose_name="Tanggal Lahir"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Alamat"
    )
    city = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Kota"
    )
    postal_code = models.CharField(
        max_length=10, 
        blank=True,
        verbose_name="Kode Pos"
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name="Bio"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def get_full_name_display(self):
        """Return full name or username if full name not available"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def get_profile_picture_url(self):
        """Return profile picture URL or default avatar"""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/img/default-avatar.png'
    
    def get_total_reviews(self):
        """Get total reviews made by user"""
        return self.review_set.count()
    
    def get_total_orders(self):
        """Get total orders (placeholder - will implement when Order model exists)"""
        # return self.order_set.count()
        return 0  # Temporary