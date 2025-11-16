from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_order_number', 'payment_method', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_method')
    search_fields = ('order__order_number', 'transaction_id')
    
    def get_order_number(self, obj):
        return obj.order.order_number if obj.order else '-'
    get_order_number.short_description = 'Order Number'