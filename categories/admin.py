from django.contrib import admin
from .models import Category
from shop.models import Product

# Inline untuk Product di dalam Category
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['name', 'price', 'stock', 'description']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [ProductInline]  # Products muncul di dalam Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock']
    list_filter = ['category']
    search_fields = ['name', 'description']