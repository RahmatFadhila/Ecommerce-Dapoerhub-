from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    """
    Format angka ke Rupiah
    Usage: {{ value|rupiah }}
    Output: Rp 150.000
    """
    try:
        value = int(value)
        return f"Rp {value:,}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"


@register.filter(name='currency')
def currency(value):
    """
    Alias untuk rupiah filter
    Usage: {{ value|currency }}
    """
    return rupiah(value)