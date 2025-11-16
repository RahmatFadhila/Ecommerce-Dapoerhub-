#shop/currency_filters.py
from django import template

register = template.Library()

@register.filter
def rupiah(value):
    """Format number to Rupiah currency"""
    try:
        # Convert to int and format with thousand separator
        return f"Rp {int(value):,}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"