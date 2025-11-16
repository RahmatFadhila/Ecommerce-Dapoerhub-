from .models import Cart

def cart_count(request):
    """
    Context processor untuk menampilkan jumlah item di cart
    di navbar (semua halaman)
    """
    count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items
        except Cart.DoesNotExist:
            count = 0
    
    return {'cart_count': count}