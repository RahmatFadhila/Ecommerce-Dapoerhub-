import midtransclient
from django.conf import settings
import hashlib

class MidtransService:
    """Service untuk handle Midtrans Snap API"""
    
    def __init__(self):
        self.snap = midtransclient.Snap(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )
        
        self.core = midtransclient.CoreApi(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )
    
    def create_transaction(self, order, payment):
        """
        Generate Snap Token untuk transaksi
        
        Args:
            order: Order object
            payment: Payment object
        
        Returns:
            dict: {'snap_token': str, 'redirect_url': str}
        """
        # Generate unique order ID
        midtrans_order_id = f"ORDER-{order.order_number}-{payment.id}"
        
        # Item details
        item_details = []
        for item in order.items.all():
            item_details.append({
                'id': str(item.product.id if item.product else 0),
                'price': int(item.product_price),
                'quantity': item.quantity,
                'name': item.product_name[:50],  # Max 50 chars
            })
        
        # Delivery fee sebagai item terpisah
        if order.delivery_fee > 0:
            item_details.append({
                'id': 'DELIVERY',
                'price': int(order.delivery_fee),
                'quantity': 1,
                'name': 'Ongkos Kirim',
            })
        
        # Customer details
        customer_details = {
            'first_name': order.customer_name[:50],
            'email': order.customer_email,
            'phone': order.customer_phone,
            'billing_address': {
                'address': order.delivery_address[:200],
                'city': order.delivery_location[:50] if order.delivery_location else 'Makassar',
                'postal_code': '90111',
                'country_code': 'IDN'
            },
            'shipping_address': {
                'address': order.delivery_address[:200],
                'city': order.delivery_location[:50] if order.delivery_location else 'Makassar',
                'postal_code': '90111',
                'country_code': 'IDN'
            }
        }
        
        # Transaction details
        transaction_details = {
            'order_id': midtrans_order_id,
            'gross_amount': int(order.total),
        }
        
        # Callbacks
        callbacks = {
            'finish': f"{settings.SITE_URL}/payments/finish/",
            'error': f"{settings.SITE_URL}/payments/error/",
            'pending': f"{settings.SITE_URL}/payments/pending/",
        }
        
        # Parameter untuk Snap API
        param = {
            'transaction_details': transaction_details,
            'item_details': item_details,
            'customer_details': customer_details,
            'callbacks': callbacks,
            'credit_card': {
                'secure': True
            },
            'enabled_payments': [
                'credit_card', 
                'bca_va', 
                'bni_va', 
                'bri_va',
                'permata_va',
                'other_va',
                'gopay', 
                'shopeepay',
                'qris',
                'akulaku'
            ],
            'expiry': {
                'unit': 'minutes',
                'duration': 1440  # 24 jam
            }
        }
        
        try:
            transaction = self.snap.create_transaction(param)
            
            # Update payment dengan snap token
            payment.midtrans_order_id = midtrans_order_id
            payment.midtrans_snap_token = transaction['token']
            payment.save()
            
            return {
                'snap_token': transaction['token'],
                'redirect_url': transaction.get('redirect_url', ''),
                'order_id': midtrans_order_id
            }
        
        except Exception as e:
            print(f"Error creating Midtrans transaction: {str(e)}")
            raise e
    
    def get_transaction_status(self, order_id):
        """
        Cek status transaksi dari Midtrans
        
        Args:
            order_id: Midtrans order ID
        
        Returns:
            dict: Transaction status response
        """
        try:
            status = self.core.transactions.status(order_id)
            return status
        except Exception as e:
            print(f"Error checking transaction status: {str(e)}")
            return None
    
    def verify_signature(self, order_id, status_code, gross_amount, server_key):
        """
        Verifikasi signature dari Midtrans notification
        
        Args:
            order_id: Order ID
            status_code: Status code dari notifikasi
            gross_amount: Gross amount
            server_key: Server key
        
        Returns:
            str: SHA512 hash
        """
        signature_string = f"{order_id}{status_code}{gross_amount}{server_key}"
        return hashlib.sha512(signature_string.encode()).hexdigest()