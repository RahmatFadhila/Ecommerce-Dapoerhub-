from django import template

register = template.Library()

@register.filter
def currency(value):
    """
    Format angka menjadi format Rupiah
    Usage: {{ price|currency }}
    Output: Rp 25.000
    """
    try:
        # Konversi ke integer dulu
        value = int(value)
        # Format dengan separator ribuan
        formatted = f"{value:,}".replace(',', '.')
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"

@register.filter
def rupiah(value):
    """
    Alias untuk currency filter
    Usage: {{ price|rupiah }}
    """
    return currency(value)