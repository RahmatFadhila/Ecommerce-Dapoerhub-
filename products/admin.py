from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Review


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ['name', 'price', 'stock', 'status', 'image']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline]
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Total Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'formatted_price_display', 
                    'stock', 'status', 'is_featured', 'average_rating', 'created_at']
    list_filter = ['category', 'status', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['image_preview', 'created_at', 'updated_at', 'rating_summary']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'status')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Review Statistics', {
            'fields': ('rating_summary',),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('is_featured', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_active', 'make_inactive', 'make_featured']
    
    def formatted_price_display(self, obj):
        return obj.formatted_price()
    formatted_price_display.short_description = 'Price'
    formatted_price_display.admin_order_field = 'price'
    
    def average_rating(self, obj):
        """Tampilkan rating rata-rata di list"""
        avg = obj.get_average_rating()
        count = obj.get_review_count()
        if avg > 0:
            stars = '⭐' * int(avg) + '☆' * (5 - int(avg))
            return format_html(
                '<span title="{} dari {} review">{} {}</span>',
                avg, count, stars, f'({avg})'
            )
        return format_html('<span style="color: #999;">Belum ada review</span>')
    average_rating.short_description = 'Rating'
    
    def rating_summary(self, obj):
        """Tampilkan detail rating di form"""
        avg = obj.get_average_rating()
        count = obj.get_review_count()
        
        if count > 0:
            # Hitung distribusi rating
            reviews = obj.reviews.filter(is_approved=True)
            rating_counts = {i: 0 for i in range(1, 6)}
            for review in reviews:
                rating_counts[review.rating] += 1
            
            html = f'<div style="font-family: monospace;">'
            html += f'<h3>Rating Summary</h3>'
            html += f'<p><strong>Average:</strong> {avg} / 5.0 ⭐</p>'
            html += f'<p><strong>Total Reviews:</strong> {count}</p>'
            html += '<hr>'
            html += '<p><strong>Rating Distribution:</strong></p>'
            
            for rating in range(5, 0, -1):
                stars = '⭐' * rating
                bar_width = (rating_counts[rating] / count * 100) if count > 0 else 0
                html += f'<div style="margin: 5px 0;">'
                html += f'{stars} ({rating}): '
                html += f'<div style="display: inline-block; width: 200px; height: 20px; background: #f0f0f0; border-radius: 3px; vertical-align: middle;">'
                html += f'<div style="width: {bar_width}%; height: 100%; background: #FFD700; border-radius: 3px;"></div>'
                html += f'</div> {rating_counts[rating]}'
                html += '</div>'
            
            html += '</div>'
            return format_html(html)
        
        return format_html('<p style="color: #999;">Belum ada review untuk produk ini.</p>')
    rating_summary.short_description = 'Rating Statistics'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No Image</span>')
    image_preview.short_description = 'Preview'
    
    def make_active(self, request, queryset):
        queryset.update(status='active')
    make_active.short_description = "Mark selected as Active"
    
    def make_inactive(self, request, queryset):
        queryset.update(status='inactive')
    make_inactive.short_description = "Mark selected as Inactive"
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark as Featured"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating_display', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['user', 'product', 'rating', 'comment', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'product', 'rating', 'comment')
        }),
        ('Moderation', {
            'fields': ('is_approved',),
            'description': 'Approve atau reject review ini. Review hanya bisa dibuat oleh user di website.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews']
    
    # ✅ DISABLE ADD PERMISSION - Admin tidak bisa add review
    def has_add_permission(self, request):
        return False
    
    # ✅ Tidak bisa delete (opsional, tapi bisa edit untuk approve/reject)
    def has_delete_permission(self, request, obj=None):
        return True  # Masih bisa delete kalau perlu
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="font-size: 18px;">{}</span> <span style="color: #666;">({})</span>',
            stars, obj.rating
        )
    rating_display.short_description = 'Rating'
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} review berhasil diapprove.')
    approve_reviews.short_description = "✅ Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} review berhasil direject.')
    reject_reviews.short_description = "❌ Reject selected reviews"